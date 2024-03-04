import asyncio
import datetime
import os
import re
import sys
from bson import ObjectId
from bson.int64 import Int64
import pymongo
from src.helpers import custom_slugify, is_english, re_write_text
from lib.mongodb import get_database
from pymongo import MongoClient, UpdateOne
import requests
import json
import traceback


def post_topic(data):
    try:
        top = asyncio.run(find_nearest_top(len(data.get("places"))))

        query = str(data.get("query")).replace(
            '"', "").replace(',', '').strip()

        d = {
            'title': f"Top {{top}} Best {query} in {{year}}",
            'metaTitle': f"Best: Top {{top}} {query}",
            'description': f'This is list of {query}',
            'metaDescription': f"Welcome to the best {{top}} {query}. This is top {{top}} {query} currently",
            'slug': custom_slugify(f"{query}"),
            'top_slug': custom_slugify(top["slug"]),
            'body': f'This is a bussiness the list of the top {{top}} {query}',
            'createdAt': datetime.datetime.now().isoformat(),
            'topId': str(top["_id"]),
            'type': "gmap_businesses",
            'status': "published",
            'lists': data.get("places")
        }

        if len(data.get("places")) >= 1:
            add_topic(d)

    except Exception as e:
        print(f"Error processing item: {str(e)}")
        traceback.print_exc()
        pass


def add_topic(data):
    lists = data["lists"]
    try:
        processed_lists = []
        db = get_database()
        col = db["topics"]
        item_details = col.find_one({'slug': data["slug"]})
        _id = ObjectId()

        if item_details is not None:
            _id = item_details["_id"]
            topic_slug = item_details["slug"]
            data["_id"] = _id
            query_filter = {'_id': data["_id"]}
            new_data = {'$set': data}
            del new_data["$set"]["lists"]
            result = col.update_one(query_filter, new_data)
            get_processed_lists = asyncio.run(
                process_list(lists, _id, topic_slug))
            for li in get_processed_lists:
                processed_lists.append(li)
        else:
            data["_id"] = _id
            new_data = data
            del new_data["lists"]
            result = col.insert_one(new_data)
            get_processed_lists = asyncio.run(
                process_list(lists, new_data["_id"], new_data["slug"]))
            for li in get_processed_lists:
                processed_lists.append(li)

        asyncio.run(add_list(processed_lists))
        generate_list_position(_id)
        print(f"{data["title"]} added to topic")
    except Exception as e:
        print(f"Error topic: {e}")
        traceback.print_exc()
        pass


async def process_list(data, topic_id, topic_slug):

    try:
        processed_lists = []
        for item in data:
            reviews = item["all_reviews"]

            pattern = re.compile(r'([^>:|-]+)\s*(?:>|\:|\-|\||\,|$)')
            match = pattern.search(item["name"])
            g_title = match.group(1) if match else item["name"]

            if item["rating"] is None:
                m_rate = 0
            else:
                m_rate = int(item["rating"]) * 10

            if item["reviews"] is None:
                r_reviews = 0
            else:
                r_reviews = int(item["reviews"])

            lang = is_english(item["about"])

            if lang == True:
                language_code = 'en'
            else:
                language_code = 'undefined'

            l_data = {
                "topicId": str(topic_id),
                "topic_slug": topic_slug,
                "title": str(g_title).strip(),
                "is_english": language_code,
                "subTitle": item["name"].strip(),
                "description": re_write_text(item["about"]),
                "body": re_write_text(item["about"]),
                "slug": custom_slugify(item["name"]),
                "rankingScore": int(str(m_rate + int(r_reviews))),
                "ratingScore": item["rating"],
                "gmap_link": item["link"],
                "type": "gmap_business",
                "address": item["address"],
                "category": item["main_category"],
                "tags": json.dumps(item["categories"]),
                "phone": item["phone"],
                "website": item["website"],
                "place_id": item["place_id"],
                "location_country": item["country"],
                "location_state": "",
                "location_city": "",
                "external_image": item["featured_image"],
                "all_images": item["all_images"],
                "detailed_reviews": item["detailed_reviews"],
                "workday_timing": json.dumps(item["workday_timing"]),
                "time_zone": item["time_zone"],
                "location": item["location"],
                "latitude": item["latitude"],
                "longitude": item["longitude"],
                "lang_long": item["lang_long"],
                "lang_short": item["lang_short"],
                "icon": item["icon"],
                "status": "published",
                "all_reviews": item["all_reviews"]
            }

            processed_lists.append(l_data)

        return processed_lists
    except Exception as e:
        print(f"Error list: {str(e)}")
        traceback.print_exc()
        pass


async def add_list(data):

    try:
        bulk = []
        processed_reviews = []
        db = get_database()
        col = db["lists"]
        for item in data:
            reviews = item["all_reviews"]
            query_filter = {'place_id': item["place_id"]}
            new_data = {'$set': item}
            del new_data["$set"]["all_reviews"]
            bulk.append(UpdateOne(query_filter, new_data, upsert=True))
            get_processed_reviews = await process_reviews(reviews, item["place_id"])
            for rev in get_processed_reviews:
                processed_reviews.append(rev)
        col.bulk_write(bulk, ordered=False)
        await add_reviews(processed_reviews)
        print(f"{len(processed_reviews)} reviews added to {len(data)} lists")
    except Exception as e:
        print(f"Error list: {str(e)}")
        traceback.print_exc()
        pass


async def process_reviews(data, list_id):
    try:
        reviews = []
        for item in data:
            lang = is_english(item["review_text"])
            if lang == True:
                language_code = 'en'
            else:
                language_code = 'undefined'

            t_data = {
                "list_id": str(list_id),
                "place_id": str(list_id),
                "is_english": language_code,
                "review_id_hash": item["review_id_hash"],
                "rating": item["rating"],
                "review_text": item["review_text"],
                "published_at": item["published_at"],
                "published_at_date": item["published_at_date"],
                "response_from_owner_text": item["response_from_owner_text"],
                "response_from_owner_ago": item["response_from_owner_ago"],
                "response_from_owner_date": item["response_from_owner_date"],
                "review_likes_count": item["review_likes_count"],
                "total_number_of_reviews_by_reviewer": item["total_number_of_reviews_by_reviewer"],
                "user_url": item["user_url"],
                "user_name": item["user_name"],
                "user_photos": item["user_photos"],
                "total_number_of_photos_by_reviewer": item["total_number_of_photos_by_reviewer"],
                "is_local_guide": item["is_local_guide"],
                "review_translated_text": item["review_translated_text"],
                "response_from_owner_translated_text": item["response_from_owner_translated_text"]
            }
            reviews.append(t_data)
        return reviews
    except Exception as e:
        print(f"Error review: {str(e)}")
        traceback.print_exc()
        pass


async def add_reviews(data):
    try:
        bulk = []
        db = get_database()
        col = db["reviews"]

        for item in data:
            query_filter = {'review_id_hash': item["review_id_hash"]}
            new_data = {'$set': item}
            bulk.append(UpdateOne(query_filter, new_data, upsert=True))
        col.bulk_write(bulk, ordered=False)
    except Exception as e:
        print(f"Error review: {str(e)}")
        traceback.print_exc()


async def find_nearest_top(length):
    try:
        if length <= 2:
            length = 2

        tops = await get_tops()

        nearest_item = min(
            tops['result'], key=lambda x: abs(int(x['top']) - length))

        return nearest_item
    except Exception as e:
        print(f"Error find_nearest_top: {str(e)}")
        traceback.print_exc()
        pass


async def get_tops():
    try:
        db = get_database()
        col = db["tops"]
        items = col.find()
        return {'result': list(items)}
    except Exception as e:
        print(f"Error get_tops: {str(e)}")
        traceback.print_exc()
        pass


def generate_list_position(topicId):
    try:
        db = get_database()
        col = db["lists"]
        item_details = col.find(
            {'topicId': str(topicId)}).sort('rankingScore', pymongo.DESCENDING)

        for index, item in enumerate(item_details):
            query_filter = {'_id': item["_id"]}
            new_data = {'$set': {'position': index + 1}}
            result = col.update_one(query_filter, new_data)
    except Exception as e:
        print(e)
        traceback.print_exc()
        pass


def get_topics_for_video(topicId):
    try:
        db = get_database()
        col = db["topics"]
        item_details = col.find(
            {'type': "blog"}).sort('rankingScore', pymongo.DESCENDING)

    except Exception as e:
        print(e)
        traceback.print_exc()
        pass

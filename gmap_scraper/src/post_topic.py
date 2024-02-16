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
from pymongo import MongoClient
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
            'slug': custom_slugify(query),
            'body': f'This is bussiness the list of the top {{top}} {query}',
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
        db = get_database()
        col = db["topics"]
        item_details = col.find_one({'slug': data["slug"]})

        if item_details is not None:
            _id = item_details["_id"]
            data["_id"] = _id
            query_filter = {'_id': data["_id"]}
            new_data = {'$set': data}
            del new_data["$set"]["lists"]
            result = col.update_one(query_filter, new_data)
            list_result = asyncio.run(add_list(lists, _id))
        else:
            _id = ObjectId()
            data["_id"] = _id
            new_data = data.copy()
            del new_data["lists"]
            result = col.insert_one(new_data)
            list_result = asyncio.run(add_list(lists, _id))

    except Exception as e:
        print(f"Error topic: {e}")
        traceback.print_exc()
        pass


async def add_list(data, topic_id):

    try:
        for item in data:
            reviews = item["detailed_reviews"]

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
                # "icon": item["icon"],
                "status": "published"
            }

            db = get_database()
            col = db["lists"]
            item_details = col.find_one({'place_id': l_data["place_id"]})

            if item_details is not None:
                query_filter = {'place_id': l_data["place_id"]}
                new_data = {'$set': l_data}
                del new_data["$set"]["detailed_reviews"]
                result = col.update_one(query_filter, new_data)
                review_result = await add_reviews(reviews, item_details["_id"])
            else:
                _id = ObjectId()
                l_data["_id"] = _id
                new_data = l_data.copy()
                del new_data["detailed_reviews"]
                result = col.insert_one(new_data)
                review_result = await add_reviews(reviews, _id)
            generate_list_position(topic_id)
    except Exception as e:
        print(f"Error list: {str(e)}")
        traceback.print_exc()
        pass


async def add_reviews(data, list_id):
    try:
        for item in data:
            lang = is_english(item["review_text"])
            if lang == True:
                language_code = 'en'
            else:
                language_code = 'undefined'

            t_data = {
                "list_id": str(list_id),
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
                "total_number_of_photos_by_reviewer": item["total_number_of_photos_by_reviewer"],
                "is_local_guide": item["is_local_guide"],
                "review_translated_text": item["review_translated_text"],
                "response_from_owner_translated_text": item["response_from_owner_translated_text"]
            }

            db = get_database()
            col = db["reviews"]
            item_details = col.find_one(
                {'review_id_hash': t_data["review_id_hash"]})

            if item_details is not None:
                query_filter = {'review_id_hash': t_data["review_id_hash"]}
                new_data = {'$set': t_data}
                result = col.update_one(query_filter, new_data)
            else:
                _id = ObjectId()
                t_data["_id"] = _id
                result = col.insert_one(t_data)
    except Exception as e:
        print(f"Error review: {str(e)}")
        traceback.print_exc()
        pass


async def find_nearest_top(length):
    try:
        if length < 5:
            length = 5
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

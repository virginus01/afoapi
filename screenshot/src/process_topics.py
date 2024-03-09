
import asyncio
import datetime
import os
import traceback
from lib.mongodb import get_database
from pymongo import MongoClient
from screenshot.src.process_lists import process_topics_lists
from screenshot.src.screenshot_taker import save_screenshot, upload_image_to_s3
from pymongo.errors import PyMongoError


def process_images(db):
    print("processing images")
    asyncio.run(process_topics_image())


async def process_topics_image():
    try:
        db = get_database()
        col = db["topics"]
        item_details = col.find({'newly_updated': {'$ne': 'no'}})
        screenshot = None
        for item in item_details:
            base = os.getenv("PROJECT_DOMAIN")
            t_path = os.getenv("TOPIC_IMAGE_PATH")
            slug = item['slug']

            image_path = f"{base}{t_path}/{slug}"
            s3_key = f"{t_path}/{slug}.png"
            screenshot = save_screenshot({'url': image_path, 'slug': slug})
            upload_image_to_s3(screenshot["path"], os.getenv(
                "NEXT_PUBLIC_AWS_BUCKET"), s3_key)

            data = {
                "newly_updated": "no",
                "generatedImagePath": s3_key,
                "imageHost": "aws-s3"
            }

            update_topic(item["_id"], data)
            process_topics_lists(item)
        if screenshot is not None:
            screenshot['driver'].quit()
    except Exception as e:
        print("An error occurred:", e)
        traceback.print_exc()
        pass
    finally:
        screenshot['driver'].quit()


def update_topic(_id, data):

    db = get_database()
    col = db["topics"]

    try:
        query_filter = {'_id': _id}
        new_data = {'$set': data}
        result = col.update_one(query_filter, new_data)

    except PyMongoError as e:
        print(f"Error updating document: {e}")
        traceback.print_exc()
        pass


import os
import traceback

from bson import ObjectId
import pymongo
from lib.mongodb import get_database
from pymongo import MongoClient
from ..src.screenshot_taker import save_screenshot, upload_image_to_s3
from pymongo.errors import PyMongoError


def process_topics_lists(data):
    print(f"processing {data["title"]} Image lists")
    try:
        db = get_database()

        if data:
            col = db["lists"]
            lists = col.find({'topicId': str(data["_id"])}) \
                .sort([('position', 1)]) \
                .limit(1000)
            bulk_operations = []
            for item in lists:
                base = os.getenv("PROJECT_DOMAIN")
                l_path = os.getenv("LIST_IMAGE_PATH")
                slug = item['slug']

                image_path = f"{base}{l_path}/{slug}"
                s3_key = f"{l_path}/{slug}.png"
                screenshot = save_screenshot({'url': image_path, 'slug': slug})
                upload_image_to_s3(screenshot["path"], os.getenv(
                    "NEXT_PUBLIC_AWS_BUCKET"), s3_key)

                list_data = {
                    "newly_updated": "no",
                    "generatedImagePath": s3_key,
                    "imageHost": "aws-s3"
                }

                query_filter = {'_id': item["_id"]}
                new_data = {'$set': list_data}
                bulk_operations.append(
                    pymongo.UpdateOne(query_filter, new_data))
            col.bulk_write(bulk_operations)
            print(f"updated lists images for {data["title"]}")
        else:
            print("list not found for", data["title"])
    except Exception as e:
        print("An error occurred:", e)
        traceback.print_exc()
        pass

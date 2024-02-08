
import os

from bson import ObjectId
from lib.mongodb import get_database
from pymongo import MongoClient
from src.screenshot_taker import save_screenshot, upload_image_to_s3
from pymongo.errors import PyMongoError



def process_topics_lists(data):
    top_id = ObjectId(data["topId"])
    
    try:
        db = get_database()
        col = db["tops"]
        top = col.find_one({'_id': top_id})
        
        if top:
            col = db["lists"]
            lists = col.find({'topicId': str(data["_id"])}) \
                        .sort([('position', 1)]) \
                        .limit(int(top["top"]))
            
            for item in lists:
                base = os.getenv("PROJECT_DOMAIN")
                l_path = os.getenv("LIST_IMAGE_PATH")
                slug = item['slug']
                
                
                image_path = f"{base}{l_path}/{slug}"
                s3_key = f"{l_path}/{slug}.png"
                screenshot = save_screenshot({'url': image_path, 'slug': slug})
                upload_image_to_s3(screenshot["path"], os.getenv(
                    "NEXT_PUBLIC_AWS_BUCKET"), s3_key)
                    
                data = {
                      "newly_updated": "no",
                      "generatedImagePath": s3_key,
                      "imageHost": "aws-s3"
                    }
                update_list(item["_id"], data)

        else:
            print("top not found for _id:", top_id)
    except Exception as e:
        print("An error occurred:", e)
        pass
        
def update_list(_id, data):

  db = get_database() 
  col = db["lists"]

  try:
    query_filter = {'_id': _id}
    new_data = {'$set': data}
    result = col.update_one(query_filter, new_data)

  except PyMongoError as e:
    print(f"Error updating list: {e}")
    pass
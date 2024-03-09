import asyncio
import os
from gmap_scraper.src.text_to_video import generate_video
from gmap_scraper.src.post_topic import post_topic
from gmap_scraper.src import Gmaps
from gmap_scraper.src.general_process import Generate
from dotenv import load_dotenv
from screenshot.src.process_topics import process_images
import os
from django.conf import settings
import boto3
from lib.mongodb import get_database
import threading


def run_gmaps_places():
    queries = ['sandwich shop in "Georgia"', 'web designers in Lagos']
    # Gmaps.places(queries, max=10, lang='en', scrape_reviews=False)
    Generate.generate_tops_in_country()


def main():
    load_dotenv()
    db = get_database()
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'api.settings')
    session = boto3.Session(
        region_name=os.getenv("NEXT_PUBLIC_AWS_REGION"),
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY")
    )
    settings.configure()

    # Create and start threads
    gmaps_thread = threading.Thread(target=run_gmaps_places)
    # process_images_thread = threading.Thread(target=process_images, args=(db,))

    gmaps_thread.start()
    # process_images_thread.start()

    # Wait for both threads to finish
    gmaps_thread.join()
    # process_images_thread.join()

    # process_images(db)


if __name__ == "__main__":
    main()

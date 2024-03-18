import asyncio
import os
import sys
from gmap_scraper.src.text_to_video import generate_video
from gmap_scraper.src.post_topic import post_topic
from gmap_scraper.src import Gmaps
from gmap_scraper.src.general_process import Generate
from dotenv import load_dotenv
from screenshot.src.process_topics import process_images, process_images_direct
import os
from django.conf import settings
import boto3
from lib.mongodb import get_database
import threading


def run_gmaps_places():
    queries = ['sandwich shop in "Georgia"',]
    # Gmaps.places(queries, max=120, lang='en', scrape_reviews=False,
    # topic_category="Sandwich Shop")
    Generate.generate_tops_in_country()


def main():
    process_image = False
    direct_image_processing = False
    load_dotenv(".env.prod")
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
    gmaps_thread.start()

    if process_image:
        process_images_thread = threading.Thread(
            target=process_images, args=(db,))
        process_images_thread.start()

    if direct_image_processing:
        process_images_direct_thread = threading.Thread(
            target=process_images_direct, args=(db,))
        process_images_direct_thread.start()

    # Wait for both threads to finish
    gmaps_thread.join()
    if process_image:
        process_images_thread.join()

    if process_image:
        process_images(db)


if __name__ == "__main__":
    main()

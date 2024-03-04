import asyncio
import os
from src.text_to_video import generate_video
from src.post_topic import post_topic
from src import Gmaps
from src.general_process import Generate
from dotenv import load_dotenv

# Generate.generate_tops_in_country()

queries = ['sandwich shop in "Georgia" ',
           'web designer in Lagos Nigeria']


Gmaps.places(queries, max=2, lang='en', scrape_reviews=False)

if __name__ == "__main__":
    load_dotenv()
    # test()
    # asyncio.run(generate_video())

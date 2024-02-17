import asyncio
from src.post_topic import post_topic
from src import Gmaps
from src.general_process import Generate

# Generate.generate_tops_in_country()

queries = ['sandwich shop in "Georgia" ',
           'sandwich shop in "Khelvachauri Municipality", Georgia']


Gmaps.places(queries, max=2, lang='en', scrape_reviews=True)

if __name__ == "__main__":
    pass

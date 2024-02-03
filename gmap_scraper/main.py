from src import Gmaps

queries = [
    "Web Designers in Nigeria",
    "Web Designers in Uk",
]

Gmaps.places(queries, max=3, lang='en', scrape_reviews=True)

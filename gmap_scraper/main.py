from src import Gmaps
from src.general_process import Generate

Generate.generate_tops_in_country()

queries = [
    "Web Designers in Nigeria",
    "Web Designers in Uk",
]
gg = ['tool store in "Croatia (Hrvatska)" ', 'tool store in "Krapina-Zagorje County", Croatia (Hrvatska)',
      'tool store in "Lika-Senj County" Croatia (Hrvatska)']

# Gmaps.places(queries, max=3, lang='en', scrape_reviews=True)

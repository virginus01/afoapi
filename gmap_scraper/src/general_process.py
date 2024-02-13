
import json
import random
import time
from src.lang import Lang
from src.gmaps import Gmaps
from lib.mongodb import get_database
from pymongo import MongoClient
from pymongo.errors import PyMongoError
import sys
import os


class Generate:

    @staticmethod
    def generate_tops_in_country():
        stop = True
        if stop is True:
            try:
                # Get the directory of the script
                script_dir = os.path.dirname(os.path.abspath(__file__))
                file_path = os.path.join(
                    script_dir, '..', '..', 'offline_database', 'countriesStateCity.txt')
                cat_file_path = os.path.join(
                    script_dir, '..', '..', 'offline_database', 'category_array.txt')

                with open(file_path, 'r', encoding='utf-8') as file:
                    file_contents = file.read()
                with open(cat_file_path, 'r', encoding='utf-8') as cat_file:
                    cat_file_contents = cat_file.read()

                try:
                    queries = []

                    data = json.loads(file_contents)
                    cat_data = json.loads(cat_file_contents)
                    random.shuffle(cat_data)
                    random.shuffle(data)
                    n = 0

                    for country in data:

                        queries.append(f"""{cat_data[0]} in "{
                            country["name"]}" """)

                        if country["states"] is not None:
                            states = country["states"]
                            random.shuffle(states)
                            for state in states:

                                queries.append(f"""{cat_data[0]} in "{
                                    state["name"]}", {country["name"]}""")

                                if state["cities"] is not None:
                                    cities = country["states"]
                                    random.shuffle(cities)
                                    for city in cities:

                                        queries.append(f"""{cat_data[0]} in "{
                                            city["name"]}" {country["name"]}""")

                                        print(queries)
                                        Gmaps.places(
                                            queries, max=3, lang=Lang.English, scrape_reviews=True)
                                        sys.exit()
                                        n += 1

                except json.JSONDecodeError as e:
                    print("Error decoding JSON:", e)
                    pass

            except Exception as e:
                print("An error occurred:", e)
                pass
            finally:
                time.sleep(5)

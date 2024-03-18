import os
import sys
import certifi
from dotenv import load_dotenv
from pymongo import MongoClient

client = None


def get_database():
    try:
        load_dotenv()
        global client  # Declare client as global to modify it within the function
        db_url = os.getenv("MONGODB_URL")

        # Create a connection using MongoClient. You can import MongoClient or use pymongo.MongoClient
        if client is None:
            if os.getenv("PRODUCTION") == "True":
                client = MongoClient(db_url, tlsCAFile=certifi.where())
            else:
                client = MongoClient(db_url)

        # Create the database for our example (we will use the same database throughout the tutorial)
        return client['topingnow']
    except Exception as e:
        print(f"mongodb connection failed: {e}")
        sys.exit()


# This is added so that many files can reuse the function get_database()
if __name__ == "__main__":
    # Get the database
    dbname = get_database()

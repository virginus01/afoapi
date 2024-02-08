from src.perform_send import click_and_send
from dotenv import load_dotenv
import os


if __name__ == "__main__":
    load_dotenv()
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'api.settings')
    click_and_send()

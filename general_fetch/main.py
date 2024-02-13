from src.general_process import Generate
from dotenv import load_dotenv
import os
from django.conf import settings
import boto3


if __name__ == "__main__":
    load_dotenv()
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'api.settings')

    # Set AWS credentials
    session = boto3.Session(
        region_name=os.getenv("NEXT_PUBLIC_AWS_REGION"),
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY")
    )
    # Configure Django settings
    settings.configure()
    # Initiate the web scraping task
    Generate.generate_tops_in_country()

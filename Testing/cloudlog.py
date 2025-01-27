from google.cloud import logging
from dotenv import load_dotenv
import os

load_dotenv()
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = '../cookiebot-bucket-key.json'

try:
    client = logging.Client()
    logger = client.logger('bot-logs')
    logger.log("hello world", severity="warning")
    print("Log message sent successfully")
except Exception as e:
    print(f"Error occurred: {e}")

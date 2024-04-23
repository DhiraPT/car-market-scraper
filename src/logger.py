from datetime import datetime
import logging
import os
from zoneinfo import ZoneInfo

from supabase import Client


def create_logger(filename: str = os.path.join('logs', datetime.now(ZoneInfo('Asia/Singapore')).strftime("%Y-%m-%d_%H-%M-%S") + '.log')):
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)

    if not os.path.exists('logs'):
        os.makedirs('logs')
    file_handler = logging.FileHandler(filename)

    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S', tz=ZoneInfo("Asia/Singapore"))
    file_handler.setFormatter(formatter)

    logger.addHandler(file_handler)


def get_logger():
    return logging.getLogger(__name__)


def upload_log_file(db: Client, filename: str):
    if os.path.getsize(filename) == 0:
        print("There are no updates to the data.")
        get_logger().info("There are no updates to the data.")

    with open(filename, 'rb') as file:
        upload_response = db.storage.from_("logs").upload(file=file, file_options={"content-type": "text/plain"})
    
    if upload_response['status'] == 201:
        print("Log file uploaded successfully to Supabase Storage.")
    else:
        print("Failed to upload log file to Supabase Storage:", upload_response['error'])

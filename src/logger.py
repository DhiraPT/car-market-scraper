from datetime import datetime
import logging

from supabase import Client


def create_logger(filename: str = datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + '.log'):
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)

    file_handler = logging.FileHandler(filename)

    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    file_handler.setFormatter(formatter)

    logger.addHandler(file_handler)


def get_logger():
    return logging.getLogger(__name__)


def upload_log_file(db: Client, filename: str):
    with open(filename, 'rb') as file:
        upload_response = db.storage.from_("logs").upload(file=filename, file_options={"content-type": "text/plain"})
    
    if upload_response['status'] == 201:
        print("Log file uploaded successfully to Supabase Storage.")
    else:
        print("Failed to upload log file to Supabase Storage:", upload_response['error'])

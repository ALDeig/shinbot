import os

from dotenv import load_dotenv

load_dotenv()

API_TOKEN = os.getenv('API_TOKEN')
ADMIN_ID = os.getenv('ADMIN_ID')
CHECK_USER_ID = os.getenv('CHECK_USER_ID')
spreadsheet_id = os.getenv('spreadsheet_id')

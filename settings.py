from dotenv import load_dotenv
load_dotenv()

import os

SECRET_KEY = os.getenv("SECRET_KEY")
MAIL_USERNAME = os.getenv("MAIL_USERNAME")
MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")

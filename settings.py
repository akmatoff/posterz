from dotenv import load_dotenv
load_dotenv()

import os

SECRET_KEY = os.getenv("SECRET_KEY")
MAIL_SERVER ='smtp.googlemail.com'
MAIL_USERNAME = os.getenv("MAIL_USERNAME")
MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
MAIL_PORT = 587
MAIL_USE_SSL = True
MAIL_USE_TLS = False
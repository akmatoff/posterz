from dotenv import load_dotenv
load_dotenv()

import os

SECRET_KEY = os.getenv("SECRET_KEY")
import os
from dotenv import load_dotenv

load_dotenv()

INSTAGRAM_USERNAME = os.getenv("INSTAGRAM_USERNAME")
INSTAGRAM_PASSWORD = os.getenv("INSTAGRAM_PASSWORD")
CHROMEDRIVER_PATH = os.getenv("CHROMEDRIVER_PATH")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

id_list = [
    "terrys_reading",
    "rdnmgo",
    "42lines_",
    "euiclee.books",
    "ai.gi.book",
]

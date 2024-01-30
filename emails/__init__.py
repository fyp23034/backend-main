from flask import Blueprint
import pymongo
import os
import openai
from dotenv import load_dotenv

dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env') # .env in root directory
load_dotenv(dotenv_path)

db_password = os.environ.get("DB_PASSWORD")

emails = Blueprint('emails', __name__)
client = pymongo.MongoClient(f'mongodb+srv://fyp23034:{db_password}@fyp23034.ckoo6oe.mongodb.net/?retryWrites=true&w=majority')

openai.api_key = os.environ.get("OPENAI_API_KEY")

from emails.routes import *
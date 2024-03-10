from flask import Flask, Blueprint, request
import pymongo
import os
from dotenv import load_dotenv
dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env') # .env in root directory
load_dotenv(dotenv_path)

db_password = os.environ.get("DB_PASSWORD")
client = pymongo.MongoClient(f'mongodb+srv://fyp23034:{db_password}@fyp23034.ckoo6oe.mongodb.net/?retryWrites=true&w=majority')
import requests
import datetime

db = client.fyp
colEmails = db.emails
colUsers = db.users
colMetrics = db.emailAiMetrics

# Iterate over the emails and update the 'receivedTime' field to epoch time
for email in colEmails.find():
    received_time = int(datetime.datetime.strptime(email['receivedTime'], '%Y-%m-%dT%H:%M:%SZ').timestamp())
    colEmails.update_one({'_id': email['_id']}, {'$set': {'receivedTime': received_time}})
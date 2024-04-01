import pymongo
from datetime import timedelta
import json
import redis

client = pymongo.MongoClient("mongodb+srv://fyp23034:hcQpJzrN@fyp23034.ckoo6oe.mongodb.net/?retryWrites=true&w=majority")
db = client.fyp
colEmails = db.emails
cache_client = redis.Redis(host='localhost', port=6379, db=0)

query = {'outlookId': 'AQMkADAwATM0MDAAMS02MjE1LTNmMjktMDACLTAwCgBGAAADdkF5WQ88-UKgjxDnLe5RlQcAqDrR27zYdkC9e-A1D1x2JwAAAgEUAAAAqDrR27zYdkC9e-A1D1x2JwAAAA_BAdQAAAA='}

get_response = cache_client.get(json.dumps(query))
if get_response:
    print('Hit!')
    print('Str', get_response)
    print('JSON', json.loads(get_response))
else:
    print("Look up resulted in a: miss.")
    dbQueryRes = colEmails.find_one(query)
    if not dbQueryRes:
        print('Email not found in DB')
    else:
        resCopy = dbQueryRes.copy()
        resCopy['_id'] = str(dbQueryRes['_id'])
        resCopy['userId'] = str(dbQueryRes['userId'])
        print(resCopy)
        cache_client.set(json.dumps(query), json.dumps(resCopy), ex=21600)
    print('DB Query Result:', dbQueryRes)
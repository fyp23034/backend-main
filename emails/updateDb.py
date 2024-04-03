import pymongo

client = pymongo.MongoClient("mongodb+srv://fyp23034:hcQpJzrN@fyp23034.ckoo6oe.mongodb.net/?retryWrites=true&w=majority")
db = client.fyp
colMetrics = db.emailAiMetrics

# update all documents in emailAiMetrics collection to have a 'cSub' and 'cBody' field, initialize to empty string
# if the field already exists, do nothing
colMetrics.update_many({}, {'$set': {'cSub': "", 'cBody': ""}})
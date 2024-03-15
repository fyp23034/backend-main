import pymongo
import universal.logic as logic

client = pymongo.MongoClient("mongodb+srv://fyp23034:hcQpJzrN@fyp23034.ckoo6oe.mongodb.net/?retryWrites=true&w=majority")
db = client.fyp

colEmails = db.emails

id = colEmails.find_one({'outlookId': 'AQMkADAwATM0MDAAMS02MjE1LTNmMjktMDACLTAwCgBGAAADdkF5WQ88-UKgjxDnLe5RlQcAqDrR27zYdkC9e-A1D1x2JwAAAgEMAAAAqDrR27zYdkC9e-A1D1x2JwAAABFtk6QAAAA='})
print(str(id['_id']))
print(logic.emailCategory(str(id['_id'])))
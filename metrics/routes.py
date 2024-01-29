from flask import Flask, Blueprint, request
from metrics import metrics, client
import requests

db = client.fyp
colEmails = db.emails
colUsers = db.users
colMetrics = db.emailAiMetrics

@metrics.route('/recordTime/<string:id>', methods=['POST'])
def updateTime(id):
    try:
        epochTime = request.json['timeSpent']
        epochTime = int(epochTime)
        currEmail = colEmails.find_one({'outlookId': id})
        currMetrics = colMetrics.find_one({'outlookId': id})
        if not currMetrics:
            colMetrics.insert_one({
                'emailId': currEmail['_id'],
                'timesClicked': 0,
                'timeSpent': epochTime,
                'outlookId': id,
                'aiScore': None
            })
        else:
            colMetrics.update_one({'outlookId': id}, {'$set': {'timeSpent': currMetrics['timeSpent'] + epochTime}})
        return {'error': False}
    except Exception as e:
        return {'error': True, 'message': e}

@metrics.route('/recordClick/<string:id>', methods=['POST'])
def recordClick(id):
    try:
        currEmail = colEmails.find_one({'outlookId': id})
        currMetrics = colMetrics.find_one({'outlookId': id})
        if not currMetrics:
            colMetrics.insert_one({
                'emailId': currEmail['_id'],
                'timesClicked': 1,
                'timeSpent': 0,
                'outlookId': id,
                'aiScore': None
            })
        else:
            colMetrics.update_one({'outlookId': id}, {'$inc': {'timesClicked': 1}})
        return {'error': False}
    except Exception as e:
        return {'error': True, 'message': e}
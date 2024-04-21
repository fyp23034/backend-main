from flask import Flask, Blueprint, request
from emails import emails, client
import redis
import json
from bson import ObjectId
import requests
from universal.getUser import getUser
import universal.logic as logic
from universal.check_spf_dmarc import check_spf_dmarc
import datetime
import threading

db = client.fyp
colEmails = db.emails
colUsers = db.users
colMetrics = db.emailAiMetrics
colIcs = db.ics


def checkRedisCache(outlookId):
    cache_client = redis.Redis(host='localhost', port=6379, db=0)
    query = {'outlookId': outlookId}
    get_response = cache_client.get(json.dumps(query))
    if get_response:    # cache hit
        cachedJson = json.loads(get_response)
        cachedJson['_id'] = ObjectId(cachedJson['_id'])
        cachedJson['userId'] = ObjectId(cachedJson['userId'])
        return cachedJson
    else:   # cache miss
        dbQueryRes = colEmails.find_one({'outlookId': outlookId})
        if not dbQueryRes:
            return None
        resCopy = dbQueryRes.copy()
        resCopy['_id'] = str(dbQueryRes['_id'])
        resCopy['userId'] = str(dbQueryRes['userId'])
        cache_client.set(json.dumps(query), json.dumps(resCopy), ex=21600)
        return dbQueryRes


def categorizeIndividualEmail(emailId, sender, userId, spfDmarcCheck=False):

    if spfDmarcCheck:
        dontAdjust, weight = check_spf_dmarc(sender['address'])
    else:
        dontAdjust, weight = True, 0

    logic.regUser(str(userId))
    aiScore = logic.emailCategory(str(emailId))
    print(aiScore)
    if not dontAdjust:
        colEmails.update_one({'_id': emailId}, {
                             '$set': {'category': (aiScore + weight) // 2}}, upsert=True)
    else:
        colEmails.update_one({'_id': emailId}, {
                             '$set': {'category': aiScore}}, upsert=True)
    return


def checkICS(emailId, userId):
    outlookId = str(emailId)
    userId = str(userId)
    logic.regUser(userId)
    success = logic.generateICS(str(outlookId))
    print(success)
    if success:
        ics_filename = f'{emailId}.ics'
        colIcs.insert_one({'emailId': ObjectId(emailId),
                          'icsFilename': ics_filename})
    return


# emailsPerPage passed by reference
def processEmail(email, userId, emailsPerPage, cacheEnabled=False):

    # TODO: Implement read-through, write-back db cache

    try:
        if not cacheEnabled:
            emailInDb = colEmails.find_one({'outlookId': email['id']})
        else:
            emailInDb = checkRedisCache(email['id'])

        # email already in database and categorized
        if emailInDb:

            emailsPerPage.append({
                'subject': emailInDb['subject'],
                'time': emailInDb['receivedTime'],
                'bodyPreview': emailInDb['bodyPreview'],
                'id': emailInDb['outlookId'],
                'sender': emailInDb['sender'],
            })
            return [True, 'Email already exists']

        '''
        email not yet in database, not yet categorized
        '''
        # get the array of recipient emails
        recipients = []
        for r in email['toRecipients']:
            recipients.append(r['emailAddress']['address'])

        insertDbObj = {
            'outlookId': email['id'],
            'userId': userId,
            'subject': email['subject'],
            'receivedTime': int(datetime.datetime.strptime(email['receivedDateTime'], '%Y-%m-%dT%H:%M:%SZ').timestamp()),
            'body': email['body']['content'],
            'cc': [],
            'bcc': [],
            'bodyPreview': email['bodyPreview'],
            'category': None,
            'recipients': recipients,
            'sender': email['sender']['emailAddress']
        }
        inserted = colEmails.insert_one(insertDbObj)

        # instantiate metrics collection
        colMetrics.insert_one({
            'emailId': inserted.inserted_id,
            'timesClicked': 0,
            'timeSpent': 0,
            'outlookId': email['id'],
            'category': None,
            'importanceScore': -1,
            'cSub': "",
            'cBody': ""
        })

        threading.Thread(target=categorizeIndividualEmail, args=(
            inserted.inserted_id, email['sender']['emailAddress'], userId,)).start()
        threading.Thread(target=checkICS, args=(
            inserted.inserted_id, userId,)).start()

        emailObj = {
            'subject': email['subject'],
            'time': int(datetime.datetime.strptime(email['receivedDateTime'], '%Y-%m-%dT%H:%M:%SZ').timestamp()),
            'bodyPreview': email['bodyPreview'],
            'sender': email['sender']['emailAddress'],
            'id': email['id'],
        }
        emailsPerPage.append(emailObj)
        return [True, 'Email added to database']
    except Exception as e:
        print(e)
        return [False, 'Something went wrong']


def updateClicks(outlookId, currEmail):
    currMetrics = colMetrics.find_one({'outlookId': outlookId})
    if not currMetrics:
        colMetrics.insert_one({
            'emailId': currEmail['_id'],
            'timesClicked': 1,
            'timeSpent': 0,
            'outlookId': outlookId,
            'aiScore': None
        })
    else:
        colMetrics.update_one({'outlookId': outlookId}, {
                              '$inc': {'timesClicked': 1}})
    return

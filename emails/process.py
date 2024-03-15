from flask import Flask, Blueprint, request
from emails import emails, client
import requests
from universal.getUser import getUser
import universal.logic as logic
import datetime
import threading

db = client.fyp
colEmails = db.emails
colUsers = db.users
colMetrics = db.emailAiMetrics

def categorizeIndividualEmail(emailId):

    # TODO: Include SPF, DKIM, DMARC, and other email security checks

    print(str(emailId))
    aiScore = logic.emailCategory(str(emailId))
    colEmails.update_one({'_id': emailId}, {'$set': {'category': aiScore}}, upsert=True)
    return

def processEmail(email, userId, emailsPerPage): # emailsPerPage passed by reference

    # TODO: Implement read-through, write-back db cache

    try:
        emailInDb = colEmails.find_one({'outlookId': email['id']})

        # email already in database and categorized
        if emailInDb:
            emailsPerPage.append({
                'subject': emailInDb['subject'],
                'time': emailInDb['receivedTime'],
                'bodyPreview': emailInDb['bodyPreview'],
                'id': emailInDb['outlookId'],
                'sender': emailInDb['sender']
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
            'importanceScore': -1
        })

        thread = threading.Thread(target=categorizeIndividualEmail, args=(inserted.inserted_id,))
        thread.start()

        emailObj = {
            'subject': email['subject'],
            'time': int(datetime.datetime.strptime(email['receivedDateTime'], '%Y-%m-%dT%H:%M:%SZ').timestamp()),
            'bodyPreview': email['bodyPreview'],
            'sender': email['sender']['emailAddress'],
            'id': email['id']
        }
        emailsPerPage.append(emailObj)
        return [True, 'Email added to database']
    except Exception as e:
        return [False, e]
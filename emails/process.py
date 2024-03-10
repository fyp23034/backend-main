from flask import Flask, Blueprint, request
from emails import emails, client
import requests
from universal.getUser import getUser
import datetime

db = client.fyp
colEmails = db.emails
colUsers = db.users
colMetrics = db.emailAiMetrics

def categorizeIndividualEmail(email):
    # should be async
    return "CALL JUSTIN'S API"

def processEmail(email, userId, emailsPerPage): # emailsPerPage passed by reference

    # TODO: Categorize email, add async support for database insertions

    try:
        emailInDb = colEmails.find_one({'outlookId': email['id']})

        # email already in database and categorized
        if emailInDb:
            emailsPerPage.append({
                'subject': emailInDb['subject'],
                'time': int(datetime.datetime.strptime(emailInDb['receivedDateTime'], '%Y-%m-%dT%H:%M:%SZ').timestamp()),
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
            'aiScore': None
        })

        # async categorization
        categorizeIndividualEmail(email)

        emailObj = {
            'subject': email['subject'],
            'time': email['receivedDateTime'],
            'bodyPreview': email['bodyPreview'],
            'sender': email['sender']['emailAddress'],
            'id': email['id']
        }
        emailsPerPage.append(emailObj)
        return [True, 'Email added to database']
    except Exception as e:
        return [False, e]
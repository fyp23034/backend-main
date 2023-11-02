from flask import Flask, Blueprint, request
from emails import emails, client
import requests
from universal.getUser import getUser
from emails.process import processEmail

db = client.fyp
colEmails = db.emails
colUsers = db.users
colMetrics = db.emailAiMetrics

@emails.route('/', methods=['GET'])
def getEmailsPerPage():
    accessToken = request.headers.get('Access-Token')
    pageNum = request.args.get('page')
    pageNum = int(pageNum)
    headers = {"Authorization": f"Bearer {accessToken}"}
    userResponse = getUser(accessToken)
    if 'error' in userResponse:
        return {'error': True, 'message': userResponse['message']}

    # save to users db
    if not colUsers.find_one({'email': userResponse['userPrincipalName']}):
        colUsers.insert_one({
            'email': userResponse['userPrincipalName'],
            'firstName': userResponse['givenName'],
            'lastName': userResponse['surname']
        })

    userEmail = userResponse['userPrincipalName']

    # get the _id field from recipient
    userId = colUsers.find_one({'email': userResponse['userPrincipalName']})['_id']

    # get the first 10 emails and process them
    endpoint = f"https://graph.microsoft.com/v1.0/me/messages?&$filter=receivedDateTime ge 1900-01-01T00:00:00Z and (not (sender/emailAddress/address eq '{userEmail}'))&$select=body,toRecipients,sender,subject,bodyPreview,receivedDateTime&$orderby=receivedDateTime desc&$skip={(pageNum-1)*50}"
    response = requests.get(endpoint,headers=headers).json()
    emailsPerPage = []
    for email in response['value']:
        processRes = processEmail(email, userId, emailsPerPage)
        print(processRes)
        if not processRes[0]:
            return {'error': True, 'message': processRes[1]}

    # get the next 40 emails and process them
    for _ in range(4):
        if '@odata.nextLink' not in response:
            break
        endpoint = response['@odata.nextLink']
        response = requests.get(endpoint,headers=headers).json()
        for email in response['value']:
            processRes = processEmail(email, userId, emailsPerPage)
            if not processRes[0]:
                return {'error': True, 'message': processRes[1]}

    return {'error': False, 'emails': emailsPerPage}

@emails.route('/<string:id>', methods=['GET'])
def getEmail(id):
    try:
        accessToken = request.headers.get('Access-Token')
        endpoint = f"https://graph.microsoft.com/v1.0/me/messages/{id}?&$select=sender,subject,body,ccRecipients,bccRecipients"
        headers = {"Authorization": f"Bearer {accessToken}"}
        response = requests.get(endpoint,headers=headers).json()
        emailObj = {
            'subject': response['subject'],
            'body': response['body']['content'],
            'cc': response['ccRecipients'],
            'bcc': response['bccRecipients'],
            'sender': response['sender']['emailAddress']
        }
        return {'error': False, 'email': emailObj}
    except:
        return {'error': True, 'message': 'Invalid access token'}

@emails.route('/getByCategory', methods=['GET'])
def getByCategory():
    try:
        accessToken = request.headers.get('Access-Token')
        userResponse = getUser(accessToken)
        if 'error' in userResponse:
            return {'error': True, 'message': userResponse['message']}
        pageNum = request.args.get('page')
        pageNum = int(pageNum)
        category = request.args.get('category')

        userId = colUsers.find_one({'email': userResponse['userPrincipalName']})['_id']

        if category == "":
            category = None
        # pageSize = 50
        pageSize = 10   # for testing purposes
        skipAmount = (pageNum-1)*pageSize
        emails = colEmails.find({'category': category, 'userId': userId}).sort('receivedTime', -1).skip(skipAmount).limit(pageSize)
        emailsPerPage = []
        for email in emails:
            emailsPerPage.append({
                'subject': email['subject'],
                'time': email['receivedTime'],
                'bodyPreview': email['bodyPreview'],
                'id': email['outlookId'],
                'sender': email['sender']
            })
        return {'error': False, 'emails': emailsPerPage}
    except Exception as e:
        return {'error': True, 'message': e}
    
@emails.route('/random')
def test():
    return {'error': False, 'random': 'random'}
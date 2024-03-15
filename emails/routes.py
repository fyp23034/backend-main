from flask import Flask, Blueprint, request
from emails import emails, client
import requests
from universal.getUser import getUser
from bs4 import BeautifulSoup
from emails.process import processEmail
import universal.logic as logic
import openai

db = client.fyp
colEmails = db.emails
colUsers = db.users
colMetrics = db.emailAiMetrics

summarizerPrompt = "You are an email summarization bot. Please summarize emails I provide you."

@emails.route('/', methods=['GET'])
def getEmailsPerPage():
    accessToken = request.headers.get('Access-Token')

    # if 'page' is not in request, default to 1
    if 'page' not in request.args:
        pageNum = 1
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
    if pageNum <= 1:    # likely a recent login so register the user in our stateless AI service
        logic.regUser(str(userId))

    # get the first n emails and process them
    endpoint = f"https://graph.microsoft.com/v1.0/me/messages?&$filter=receivedDateTime ge 1900-01-01T00:00:00Z and (not (sender/emailAddress/address eq '{userEmail}'))&$select=body,toRecipients,sender,subject,bodyPreview,receivedDateTime&$orderby=receivedDateTime desc&$skip={(pageNum-1)*50}&$count=true"
    response = requests.get(endpoint,headers=headers).json()
    totalEmails = response['@odata.count']
    emailsPerPage = []
    for email in response['value']:
        processRes = processEmail(email, userId, emailsPerPage)
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

    return {'error': False, 'emails': emailsPerPage, 'totalEmails': totalEmails}

@emails.route('/<string:id>', methods=['GET'])
def getEmail(id):
    try:
        accessToken = request.headers.get('Access-Token')
        endpoint = f"https://graph.microsoft.com/v1.0/me/messages/{id}?&$select=sender,subject,body,ccRecipients,bccRecipients"
        headers = {"Authorization": f"Bearer {accessToken}"}
        response = requests.get(endpoint,headers=headers).json()
        if 'error' in response:
            return {'error': True, 'message': response['error']['message']}, 500
        emailObj = {
            'subject': response['subject'],
            'body': response['body']['content'],
            'cc': response['ccRecipients'],
            'bcc': response['bccRecipients'],
            'sender': response['sender']['emailAddress']
        }
        return {'error': False, 'email': emailObj}
    except Exception as e:
        print(e)
        return {'error': True, 'message': 'Invalid access token'}, 500

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
        pageSize = 50
        # pageSize = 10   # for testing purposes
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
        return {'error': False, 'emails': emailsPerPage, 'totalEmails': len(emailsPerPage)}
    except Exception as e:
        print(e)
        return {'error': True, 'message': 'Invalid cateogyr or database error'}
    
# some test route for testing purposes only
@emails.route('/test')
def test():
    return {'error': False}

@emails.route('/changeCategory/<string:id>', methods=['POST'])
def changeCategory(id):
    try:
        outlookId = id
        category = request.json['newCategory']
        colEmails.update_one({'outlookId': outlookId}, {'$set': {'category': category}})
        return {'error': False}
    except Exception as e:
        print(e)
        return {'error': True, 'message': 'Invalid email ID or database error'}

@emails.route('/getSummary/<string:id>', methods=['GET'])
def summarise(id):
    try:
        # GET THE EMAIL BODY HERE
        email = colEmails.find_one({'outlookId': id})
        body = email['body']

        # use beautiful soup to remove html tags
        soup = BeautifulSoup(body, 'html.parser')
        body = soup.get_text()

        # CALL THE SUMMARISATION API HERE
        prompt = [{"role": "system", "content": summarizerPrompt}, {"role": "user", "content": body}]
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=prompt,
            temperature=0.7,
            presence_penalty=0,
            max_tokens=1000
        )
        return {'error': False, 'summary': str(response["choices"][0]["message"]["content"])}
    except Exception as e:
        print(e)
        return {'error': True, 'message': 'Something went wrong or this email has no summarizable body'}
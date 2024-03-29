from flask import Flask, Blueprint, request, send_file
from emails import emails, client
import requests
from universal.getUser import getUser
from bson import ObjectId
from bs4 import BeautifulSoup
from emails.process import processEmail, updateClicks
import universal.logic as logic
import time
import openai
import threading

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
    cnt = 0
    foundInDb = False
    for email in response['value']:
        processRes = processEmail(email, userId, emailsPerPage)
        if not processRes[0]:
            return {'error': True, 'message': processRes[1]}
        elif processRes[1] == 'Email already exists':
            # email already found in the database, so we just need to get the next 10 - cnt emails
            nextFew = colEmails.find({'userId': userId}).sort('receivedTime', -1).skip((50 * (pageNum - 1)) + cnt + 1).limit(50)
            foundInDb = True
            break
        cnt += 1
    
    if foundInDb:
        currLen = len(emailsPerPage)
        for email in nextFew:
            if currLen >= 50:
                break
            emailsPerPage.append({
                'subject': email['subject'],
                'time': email['receivedTime'],
                'bodyPreview': email['bodyPreview'],
                'id': email['outlookId'],
                'sender': email['sender']
            })
            currLen += 1

    if not foundInDb:
        # get the next 40 emails and process them
        cnt = 10
        foundInDbSecondRound = False
        for _ in range(4):
            if '@odata.nextLink' not in response:
                break
            if foundInDbSecondRound:
                break
            endpoint = response['@odata.nextLink']
            response = requests.get(endpoint,headers=headers).json()
            for email in response['value']:
                processRes = processEmail(email, userId, emailsPerPage)
                if not processRes[0]:
                    return {'error': True, 'message': processRes[1]}
                elif processRes[1] == 'Email already exists':
                    nextFew = colEmails.find({'userId': userId}).sort('receivedTime', -1).skip((50 * (pageNum - 1)) + cnt + 1).limit(50)
                    foundInDbSecondRound = True
                    break
                cnt += 1
        
        if foundInDbSecondRound:
            currLen = len(emailsPerPage)
            for email in nextFew:
                if currLen >= 50:
                    break
                emailsPerPage.append({
                    'subject': email['subject'],
                    'time': email['receivedTime'],
                    'bodyPreview': email['bodyPreview'],
                    'id': email['outlookId'],
                    'sender': email['sender']
                })
                currLen += 1

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
        currEmail = colEmails.find_one({'outlookId': id})
        aiScore = currEmail['category']
        threading.Thread(target=updateClicks, args=(id, currEmail)).start() # update clicks using multithreading
        score = 0
        # if category is from 0-3, score = 1. if category is from 4-7, score = 2. if category is from 8-10, score = 3
        if aiScore in range(0, 4):
            score = 1
        elif aiScore in range(4, 8):
            score = 2
        elif aiScore in range(8, 11):
            score = 3
        emailObj = {
            'subject': response['subject'],
            'body': response['body']['content'],
            'cc': response['ccRecipients'],
            'bcc': response['bccRecipients'],
            'sender': response['sender']['emailAddress'],
            'category': score
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
        category = int(category)

        userId = colUsers.find_one({'email': userResponse['userPrincipalName']})['_id']

        if category == 1:
            lowerBound = 0
            upperBound = 3
        elif category == 2:
            lowerBound = 4
            upperBound = 7
        elif category == 3:
            lowerBound = 8
            upperBound = 10

        pageSize = 50
        # pageSize = 10   # for testing purposes
        skipAmount = (pageNum-1)*pageSize
        emails = colEmails.find({'category': {'$gte': lowerBound, '$lte': upperBound}, 
                                 'userId': userId}).sort('receivedTime', -1).skip(skipAmount).limit(pageSize)
        emailsPerPage = []
        emailCount = colEmails.count_documents({'category': {'$gte': lowerBound, '$lte': upperBound}, 'userId': userId})
        for email in emails:
            emailsPerPage.append({
                'subject': email['subject'],
                'time': email['receivedTime'],
                'bodyPreview': email['bodyPreview'],
                'id': email['outlookId'],
                'sender': email['sender']
            })
        return {'error': False, 'emails': emailsPerPage, 'totalEmails': emailCount}
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
        category = int(category)
        if category == 1:
            setCat = 2
        elif category == 2:
            setCat = 5
        elif category == 3:
            setCat = 9
        colEmails.update_one({'outlookId': outlookId}, {'$set': {'category': setCat}})
        return {'error': False}
    except Exception as e:
        print(e)
        return {'error': True, 'message': 'Invalid email ID or database error'}

@emails.route('/dailySummary', methods=['GET'])
def getDailySummary():
    # get the epoch time 24 hours ago
    try:
        accessToken = request.headers.get('Access-Token')
        userResponse = getUser(accessToken)
        if 'error' in userResponse:
            return {'error': True, 'message': userResponse['message']}
        userId = colUsers.find_one({'email': userResponse['userPrincipalName']})['_id']
        logic.regUser(str(userId))
        epochTime = int(time.time())
        epochTime -= 86400
        summary = logic.dailySummary(epochTime)
        return {'error': False, 'summary': summary}
    except Exception as e:
        print(e)
        return {'error': True, 'message': 'Something went wrong with the AI summarise function'}

@emails.route('/generateICS/<string:id>', methods=['GET'])
def generateICS(id):
    try:
        email = colEmails.find_one({'outlookId': id})
        emailId = str(email['_id'])
        userId = str(email['userId'])
        logic.regUser(userId)
        success = logic.generateICS(str(emailId))
        if success:
            ics_filename = f'{emailId}.ics'
            return send_file(ics_filename, as_attachment=True)
        return {'error': True, 'message': 'Something went wrong with the ICS generation function'}
    except Exception as e:
        print(e)
        return {'error': True, 'message': 'Something went wrong with the ICS generation function'}

# omit for now, will implement in the future
@emails.route('/smartSearch', methods=['POST'])
def smartSearch():
    try:
        accessToken = request.headers.get('Access-Token')
        searchString = request.json['searchString']
        userResponse = getUser(accessToken)
        if 'error' in userResponse:
            return {'error': True, 'message': userResponse['message']}
        userId = colUsers.find_one({'email': userResponse['userPrincipalName']})['_id']
        logic.regUser(str(userId))
        emailIdList = logic.smartSearch(searchString)
        # change emailIdList to ObjectId
        emailIdList = [ObjectId(emailId) for emailId in emailIdList]
        emailsInDb = colEmails.find({'_id': {'$in': emailIdList}})

        emailReturnList = []
        for email in emailsInDb:
            emailReturnList.append({
                'subject': email['subject'],
                'time': email['receivedTime'],
                'bodyPreview': email['bodyPreview'],
                'id': email['outlookId'],
                'sender': email['sender']
            })
        return {'error': False, 'emails': emailReturnList, 'totalEmails': len(emailReturnList)}
    except Exception as e:
        print(e)
        return {'error': True, 'message': 'Something went wrong with the smart search function'}

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
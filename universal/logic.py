from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from pymongo import MongoClient
from bson import ObjectId
from icalendar import Calendar, Event
from datetime import datetime
import pytz
import openai
from datetime import datetime

client = MongoClient("mongodb+srv://fyp23034:hcQpJzrN@fyp23034.ckoo6oe.mongodb.net/?retryWrites=true&w=majority")
db = client.fyp
Emails = []
currentUserID = ""

class Email:
    def __init__(self, subject, timeReceived, body, senderName, senderAddress, cc, bcc, timesClicked, timeSpent, to, emailID, userID, importanceScore, category, real):
        self.subject = subject.replace('\r', ' ').replace('\n', ' ')
        self.timeReceived = timeReceived
        body = body.replace('\r', ' ').replace('\n', ' ')
        self.body = ' '.join(''.join(char for char in body if 32 <= ord(char) <= 126).split())
        self.senderName = senderName
        self.senderAddress = senderAddress
        self.cc = cc
        self.bcc = bcc
        self.timesClicked = timesClicked
        self.timeSpent = timeSpent
        self.to = to
        self.emailID = str(emailID)
        self.userID = str(userID)
        self.importanceScore = importanceScore
        self.category = category
        self.real = real

    def printInfo(self):
        print('Subject:', self.subject)
        print('Time Received:', self.timeReceived)
        print('Body:', self.body)
        print('Sender Name:', self.senderName)
        print('Sender Address:', self.senderAddress)
        print('CC:', self.cc)
        print('BCC:', self.bcc)
        print('Times Clicked:', self.timesClicked)
        print('Time Spent:', self.timeSpent)
        print('To:', self.to)
        print('Email ID:', self.emailID)
        print('User ID:', self.userID)
        print('Importance Score:', self.importanceScore)
        print('Category:', self.category)
        print('Real:', self.real)


def calculate_similarity(text1, text2):
    # Convert the text into TF-IDF vectors
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform([text1, text2])
    # Compute the cosine similarity
    similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])
    return similarity[0][0]

def similarity_score(atr, current_email):
      score = 0
      for Email in Emails:
          score += calculate_similarity(getattr(Email,atr),getattr(current_email,atr))*getattr(Email,"timeSpent")
      return score

def create_ics_file(summary, start_datetime, end_datetime, location, details, file_name):
    cal = Calendar()
    cal.add('prodid', '-//Custom Calendar Event//mxm.dk//')
    cal.add('version', '2.0')
    event = Event()
    event.add('summary', summary)
    event.add('dtstart', start_datetime)
    event.add('dtend', end_datetime)
    event.add('location', location)
    event.add('description', details)
    event['uid'] = f"{start_datetime.strftime('%Y%m%dT%H%M%S')}@emailefficiencybooster"
    event.add('priority', 5)
    cal.add_component(event)
    with open(file_name, 'wb') as ics_file:
        ics_file.write(cal.to_ical())

def getMongoDBData():
    Emails.clear()
    #add 'emails' & 'fyp.emailAiMetrics' information
    pipeline = [
        {
            '$match': {
                'userId': ObjectId(currentUserID)
            }
        },
        {
            '$lookup': {
                'from': 'emailAiMetrics',
                'localField': '_id',
                'foreignField': 'emailId',
                'as': 'activity'
            }
        }
    ]
    jd = list(db.emails.aggregate(pipeline))
    for i in range(len(jd)):
        Emails.append(Email(jd[i]['subject'],jd[i]['receivedTime'],jd[i]['bodyPreview'],jd[i]['sender']['name'],jd[i]['sender']['address'],jd[i]['cc'],jd[i]['bcc'],jd[i]['activity'][0]['timesClicked'],jd[i]['activity'][0]['timeSpent'],jd[i]['recipients'],jd[i]['_id'],jd[i]['userId'],jd[i]['activity'][0]['importanceScore'],jd[i]['activity'][0]['category'],True))

    #add 'fakeEmails' information
    fakeEmails = list(db.fakeEmails.find({"userId": ObjectId(currentUserID)}))
    for i in range(len(fakeEmails)):
        Emails.append(Email(fakeEmails[i]['subject'],fakeEmails[i]['timeReceived'],fakeEmails[i]['body'],fakeEmails[i]['senderName'],fakeEmails[i]['senderAddress'],fakeEmails[i]['cc'],fakeEmails[i]['bcc'],fakeEmails[i]['timesClicked'],fakeEmails[i]['timeSpent'],None,None,None,None,None,False))

#addNewRecordsToFakeEmails("654279c91f4bb5264eb7303d", "subject", "", "body", "", "", [], [], 2, 40)
def addNewRecordsToFakeEmails(userId, subject, timeReceived, body, senderName, senderAddress, cc, bcc, timesClicked, timeSpent):
    record = {
        "userId": userId,
        "subject": subject,
        "timeReceived": timeReceived,
        "body": body,
        "senderName": senderName,
        "senderAddress": senderAddress,
        "cc": cc,
        "bcc": bcc,
        "timesClicked": timesClicked,
        "timeSpent": timeSpent
    }
    db.fakeEmails.insert_one(record)



#print("Importance score: " , importanceScore(Email("I hate FYP","","Job offer letter is attached in this email!","","",[],[],0,0,None,None,None,None,None,None)))
def importanceScore(ce):
    return similarity_score("subject",ce)

def askGPT(question):

    try:
        response = openai.Completion.create(
            engine="gpt-3.5-turbo-instruct",
            prompt=question,
            max_tokens=1000
        )
        return response.choices[0].text.strip()
    except Exception as e:
        return str(e)

#emailIDToEmailObject("65427c82d747ca686fa7382f")
def emailIDToEmailObject(emailID):
    for Email in Emails:
        if str(Email.emailID) == emailID:
            return Email
    return None




#_______________________________________________________________________________________________________________________

def regUser(userID):
    global currentUserID
    currentUserID = userID
    getMongoDBData()

def emailSummarization(emailID):
    subject = str(emailIDToEmailObject(emailID).subject)
    body = str(emailIDToEmailObject(emailID).body)
    return askGPT("Summarize the email blow in a third person tone and cut it short as short as possible. \nSubject: \"" + subject + "\" \nBody: \"" + body + "\"")


def emailCategory(emailID):
    score = importanceScore(emailIDToEmailObject(emailID))
    db.emailAiMetrics.update_one({"emailId": ObjectId(emailID)}, {"$set": {"importanceScore": score}})

    otherEmailsScore = []
    for Email in Emails:
        if (Email.real) and (Email.emailID != emailID) and (int(Email.importanceScore) != -1):
            otherEmailsScore.append(float(Email.importanceScore))

    otherEmailsScore.append(score)
    rank = sorted(otherEmailsScore, reverse=True).index(score) + 1

    relativeRank = rank / len(otherEmailsScore)  # from 0 to 1, the smaller the number, the higher the rank in importance level

    if relativeRank <= 0.1:
        category = 1
    elif relativeRank <= 0.2:
        category = 2
    elif relativeRank <= 0.3:
        category = 3
    elif relativeRank <= 0.4:
        category = 4
    elif relativeRank <= 0.5:
        category = 5
    elif relativeRank <= 0.6:
        category = 6
    elif relativeRank <= 0.7:
        category = 7
    elif relativeRank <= 0.8:
        category = 8
    elif relativeRank <= 0.9:
        category = 9
    else:
        category = 10

    tmp = list(db.whiteList.find({"userId": ObjectId(currentUserID)}, {"email": 1, "_id": 0}))
    WhiteList = [d['email'] for d in tmp]

    for wEmails in WhiteList:
        if str(wEmails) == str(emailIDToEmailObject(emailID).senderAddress):    #is whitelist
            category = 11

    db.emailAiMetrics.update_one({"emailId": ObjectId(emailID)}, {"$set": {"category": category}})
    return category


#addToWhiteList("abc@hku.hk")
def addToWhiteList(email):
    record = {
        "email": email,
        "userId": ObjectId(currentUserID)
    }
    db.whiteList.insert_one(record)

#userNLR("I want emails related to job, interview, and offers to assign a higher importance rating")
def userNLR(req):
    words = askGPT("I am working on an email system that determines an important rating for each email. The user specifies his preference of emails in a string: \"" + req + "\". Give me at least 10 words that might appear in the related emails. Only specify the words seperated with space in a line, do not include other sentences.")
    direction = askGPT("I am working on an email system that determines an important rating for each email. The user specifies his preference of emails in a string: \"" + req + "\". Give me a -100 to 100 rating of how the user thinks those emails are important. Only specify the answer, do not include other sentences.")
    direction = int(direction)
    addNewRecordsToFakeEmails(ObjectId(currentUserID), words, "", words, "", "", [], [], 1, direction)
































































































def generateICS(emailID):
    subject = str(emailIDToEmailObject(emailID).subject)
    time_received = str(emailIDToEmailObject(emailID).timeReceived)
    body = str(emailIDToEmailObject(emailID).body)
    sender_name = str(emailIDToEmailObject(emailID).senderName)



    print("\n\nTopic:")
    print(askGPT("Here is an email I just received with information below.\nSubject: \"" + subject + "\"\nTime Received: \"" + str(datetime.fromtimestamp(int(time_received)).strftime('%c')) + "\"\nBody: \"" + body + "\"\nSender name: \"" + sender_name + "\"\n\nOutput a topic for the event mentioned without mentioning the location, date and time. Only output the topic itself, without including any other words like \"Topic:\"."))
    print("\n\nStart:")
    print(askGPT("Here is an email with information below.\nSubject: \"" + subject + "\"\nTime Received: \"" + str(datetime.fromtimestamp(int(time_received)).strftime('%c')) + "\"\nBody: \"" + body + "\"\nSender name: \"" + sender_name + "\"\n\nOnly Give me the event's starting time with exact date and time (format \"YYYY-MM-DD-HH-MM\") for it."))
    print("\n\nDuration:")
    print(askGPT("Here is an email with information below.\nSubject: \"" + subject + "\"\nTime Received: \"" + str(datetime.fromtimestamp(int(time_received)).strftime('%c')) + "\"\nBody: \"" + body + "\"\nSender name: \"" + sender_name + "\"\n\nOnly Give me the event's ending time with exact date and time (format \"YYYY-MM-DD-HH-MM\") for it."))
    print("\n\nLocation:")
    print(askGPT("Here is an email with information below.\nSubject: \"" + subject + "\"\nTime Received: \"" + str(datetime.fromtimestamp(int(time_received)).strftime('%c')) + "\"\nBody: \"" + body + "\"\nSender name: \"" + sender_name + "\"\n\nOutput only the location for this event."))
    # summary = 'My Special Event'
    # start_datetime = datetime(2024, 3, 14, 18, 0, 0, tzinfo=pytz.utc)
    # end_datetime = datetime(2024, 3, 14, 20, 0, 0, tzinfo=pytz.utc)
    # location = '123 Event Location St, City, Country'
    # details = 'This is a detailed description of my special event. Join us for fun and learning!'
    # create_ics_file(summary, start_datetime, end_datetime, location, details, 'my_special_event.ics')

def health():
    return "OK"
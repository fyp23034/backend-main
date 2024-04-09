from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from pymongo import MongoClient
from bson import ObjectId
from icalendar import Calendar, Event
from datetime import datetime
import pytz
import openai
from datetime import datetime
from bs4 import BeautifulSoup, MarkupResemblesLocatorWarning
import spacy
import warnings
import re
import os

warnings.filterwarnings("ignore", category=MarkupResemblesLocatorWarning)
client = MongoClient("mongodb+srv://fyp23034:hcQpJzrN@fyp23034.ckoo6oe.mongodb.net/?retryWrites=true&w=majority")
db = client.fyp
Emails = []
currentUserID = ""

class Email:
    def __init__(self, subject, timeReceived, body, senderName, senderAddress, cc, bcc, timesClicked, timeSpent, to, emailID, userID, importanceScore, category, real, csub, cbody):
        self.subject = subject.replace('\r', ' ').replace('\n', ' ')
        self.timeReceived = timeReceived
        body = body.replace('\r', ' ').replace('\n', ' ')
        body = ' '.join(''.join(char for char in body if 32 <= ord(char) <= 126).split())
        soup = BeautifulSoup(body,"html.parser")
        body = soup.get_text()
        self.body = body
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
        self.csub = csub
        self.cbody = cbody

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
        print('Cleaned Subject:', self.csub)
        print('Cleaned Body:', self.cbody)

def cleanText(text):
    ban_punc = [',', '.', '?', '!', '(', ')', ';', ':', '@', '#', '$', '%', '&', '-', '/']
    for punctuation in ban_punc:
        text = text.replace(punctuation, " ")
    nlp = spacy.load('en_core_web_sm')
    doc = nlp(text)
    filtered_lemmatized_tokens = [token.lemma_ for token in doc if not token.is_stop]
    text = ' '.join(filtered_lemmatized_tokens).lower()
    text = re.sub(r'\s+', ' ', text)
    return text

def sameSender(email1, email2):
    return (email1==email2)

def sameDomain(email1, email2):
    at_pos = email1.find('@') + 1
    email1 = email1[at_pos:]
    at_pos = email2.find('@') + 1
    email2 = email2[at_pos:]
    return (email1==email2)

def calculate_similarity_for_sentences(text1, text2):
    try:
        if (text1 == "") or (text2 == ""):
            return 0
        # Convert the text into TF-IDF vectors
        vectorizer = TfidfVectorizer()
        tfidf_matrix = vectorizer.fit_transform([text1, text2])
        # Compute the cosine similarity
        similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])
        return similarity[0][0]
    except Exception as e:
        return 0

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
    folder_path = os.path.join(os.getcwd(), "ics")
    os.makedirs(folder_path, exist_ok=True)
    file_path = os.path.join(folder_path, file_name)
    with open(file_path, 'wb') as ics_file:
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
        Emails.append(Email(jd[i]['subject'],jd[i]['receivedTime'],jd[i]['body'],jd[i]['sender']['name'],jd[i]['sender']['address'],jd[i]['cc'],jd[i]['bcc'],jd[i]['activity'][0]['timesClicked'],jd[i]['activity'][0]['timeSpent'],jd[i]['recipients'],jd[i]['_id'],jd[i]['userId'],jd[i]['activity'][0]['importanceScore'],jd[i]['activity'][0]['category'],True,jd[i]['activity'][0]['cSub'],jd[i]['activity'][0]['cBody']))

    #add 'fakeEmails' information
    fakeEmails = list(db.fakeEmails.find({"userId": ObjectId(currentUserID)}))
    for i in range(len(fakeEmails)):
        Emails.append(Email(fakeEmails[i]['subject'],fakeEmails[i]['timeReceived'],fakeEmails[i]['body'],fakeEmails[i]['senderName'],fakeEmails[i]['senderAddress'],fakeEmails[i]['cc'],fakeEmails[i]['bcc'],fakeEmails[i]['timesClicked'],fakeEmails[i]['timeSpent'],None,None,None,None,None,False,"",""))




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

#print("Importance score: " , importanceScore(Email("I hate FYP","","Job offer letter is attached in this email!","","",[],[],0,0,None,None,None,None,None,None,"","")))
def importanceScore(ce):
    score = 0
    for Email in Emails:
        if Email.real:
            email_sub = Email.csub
            email_body = Email.cbody
        else:
            email_sub = Email.subject
            email_body = Email.body
        ce_sub = ce.csub
        ce_body = ce.cbody
        old_email_estimated_importance = 1.06536990187897 + 15.6984297986334*Email.timeSpent/len(Email.body) + 1.99765035579357*Email.timesClicked
        similarity = 0.3 + 0.135774138397806*calculate_similarity_for_sentences(email_sub, ce_sub) + 0.174145285454568*calculate_similarity_for_sentences(email_body, ce_body) + 0.478739220936705*sameDomain(ce.senderAddress, Email.senderAddress) + 0.0859515885173441*sameSender(ce.senderAddress, Email.senderAddress)
        score += similarity * old_email_estimated_importance
    score = score/len(Emails)
    return score

def askGPT(question):

    try:
        response = openai.Completion.create(
            engine="gpt-3.5-turbo-instruct",
            prompt=question,
            max_tokens=1000
        )
        return str(response.choices[0].text.strip())
    except Exception as e:
        return str(e)

#emailIDToEmailObject("65427c82d747ca686fa7382f")
def emailIDToEmailObject(emailID):
    for Email in Emails:
        if str(Email.emailID) == emailID:
            return Email
    return None




#_______________________________________________________________________________________________________________________

#used whenever new emails arrived
def regUser(userID):
    global currentUserID
    currentUserID = userID
    getMongoDBData()
    collection = db.emailAiMetrics
    for Email in reversed(Emails):
        if (Email.real):
            emailID = Email.emailID
            if emailID is not None:
                record = collection.find_one({"emailId": ObjectId(emailID)}, {'cSub': 1, 'cBody': 1})
                if record:
                    if record['cSub'] == "":
                        cleaned = cleanText(Email.subject)
                        collection.update_one({"emailId": ObjectId(emailID)}, {'$set': {'cSub': cleaned}})
                        Email.cSub = cleaned
                    if record['cBody'] == "":
                        cleaned = cleanText(Email.body)
                        collection.update_one({"emailId": ObjectId(emailID)}, {'$set': {'cBody': cleaned}})
                        Email.cBody = cleaned
                    if (record['cSub'] != "") or (record['cBody'] != ""):
                        break

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

def parse_datetime(st_str):
    formats = ["%Y-%m-%d-%H-%M", "%Y-%m-%d-%H%M"]
    for fmt in formats:
        try:
            return datetime.strptime(st_str, fmt)
        except ValueError:
            continue
    raise None

#output True/False. True: .ics generated succuessfully at the same folder with name 'emailID'.ics. False: .ics generation failed
#generateICS("65427c82d747ca686fa7382f")
def generateICS(emailID):
    try:
        subject = str(emailIDToEmailObject(emailID).subject)
        time_received = str(emailIDToEmailObject(emailID).timeReceived)
        body = str(emailIDToEmailObject(emailID).body)
        sender_name = str(emailIDToEmailObject(emailID).senderName)
        topic = askGPT(
            "Here is an email I just received with information below.\nSubject: \"" + subject + "\"\nTime Received: \"" + str(
                datetime.fromtimestamp(int(time_received)).strftime(
                    '%c')) + "\"\nBody: \"" + body + "\"\nSender name: \"" + sender_name + "\"\n\nOutput a topic for the event mentioned without mentioning the location, date and time. Only output the topic itself, without including any other words like \"Topic:\".")
        if (topic[0] == '"') and (topic[-1] == '"'):
            topic = topic[1:-1]
        st_str = askGPT(
            "Answer my question with this format \"YYYY-MM-DD-HH-MM\"(do not use \':\') without any other words.\n Here is an email with information below.\nSubject: \"" + subject + "\"\nTime Received: \"" + str(
                datetime.fromtimestamp(int(time_received)).strftime(
                    '%c')) + "\"\nBody: \"" + body + "\"\nSender name: \"" + sender_name + "\"\n\nGive me the event's starting time with exact date and time.")
        start_datetime = parse_datetime(st_str)
        et_str = askGPT(
            "Answer my question with this format \"YYYY-MM-DD-HH-MM\"(do not use \':\') without any other words.\n Here is an email with information below.\nSubject: \"" + subject + "\"\nTime Received: \"" + str(
                datetime.fromtimestamp(int(time_received)).strftime(
                    '%c')) + "\"\nBody: \"" + body + "\"\nSender name: \"" + sender_name + "\"\n\nGive me the event's ending time with exact date and time.")
        end_datetime = parse_datetime(et_str)
        location = askGPT(
            "Here is an email with information below.\nSubject: \"" + subject + "\"\nTime Received: \"" + str(
                datetime.fromtimestamp(int(time_received)).strftime(
                    '%c')) + "\"\nBody: \"" + body + "\"\nSender name: \"" + sender_name + "\"\n\nOutput only the location for this event without any other words.")
        location = location.replace("Location: ", "")
        location = location.replace("location: ", "")
        location = location.replace("Location:", "")
        location = location.replace("location:", "")
        create_ics_file(topic, start_datetime, end_datetime, location, "", emailID + '.ics')
        return True
    except Exception as e:
        return False

#output lists of emailIDs
def smartSearch(request):
    relatedWords = askGPT("A user search emails with the string: \"" + request + "\". Please give me at least 10 vocabularies that might also appear in the target emails.")
    relatedWords = relatedWords.replace(". ", "")
    for i in range(10):
        relatedWords = relatedWords.replace(str(i), "")
    relatedWords = cleanText(relatedWords + " " + request + " " + request + " " + request)

    relatedEmails = []
    for Email in Emails:
        if (Email.real):
            if (calculate_similarity_for_sentences(Email.csub,relatedWords) > 0):
                relatedEmails.append(Email.emailID)
    return relatedEmails

#suggestReply("65427c82d747ca686fa7382f", "accept the interview")
#return a string
def suggestReply(emailID, command):
    emailContent = emailIDToEmailObject(emailID).body
    reply = askGPT("I am developing an email reply suggestion function, the user wants to reply the below email with the request \"" + command + "\". The to be replied email's content is attached below. Generate a reply for the below email.\n\nEmail Received:\n" + emailContent)
    dearpos = reply.find("Dear")
    hipos = reply.find("Hi")
    if (dearpos >= 0) and (hipos >= 0):
        pos = min(dearpos,hipos)
    elif (dearpos >= 0) and (hipos < 0):
        pos = dearpos
    elif (dearpos < 0) and (hipos >= 0):
        pos = hipos
    else:
        pos = -1
    if pos >= 0:
        reply = reply[pos:]
    return reply

#dailySummary(1710647345)
def dailySummary(fromTime):
    noEmails = True
    gptRequest = "Please make a summary from the below emails in a third person perspective like \"You just received an email about...\". Below are the list of emails to be summarized.\n----------------------------------------------\n"
    for Email in Emails:
        if (Email.category != None):
            if (Email.real):
                if (Email.timeReceived >= fromTime) and ((Email.category <= 4) or (Email.category == 11)):
                    noEmails = False
                    gptRequest += Email.body + "\n----------------------------------------------\n"
    if noEmails:
        return "You got no important emails today. Have a good day!"
    else:
        return askGPT(gptRequest)

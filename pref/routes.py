from flask import Flask, Blueprint, request
from pref import pref, client
import requests
from universal.getUser import getUser
import universal.logic as logic
from pref.obtainPreferences import obtainPreferences

db = client.fyp
colEmails = db.emails
colUsers = db.users
colPref = db.userPreferences

@pref.route('/getPreferences', methods=['GET'])
def getPref():
    try:
        accessToken = request.headers.get('Access-Token')
        userResponse = getUser(accessToken)
        if 'error' in userResponse:
            return userResponse
        userEmail = userResponse['userPrincipalName']
        currPref = obtainPreferences(userEmail)
        return {'error': False, 'prefList': currPref['prefList'], 'whitelist': currPref['whitelist']}
    except Exception as e:
        return {'error': True, 'message': e}

@pref.route('/updatePreferences', methods=['POST'])
def updatePref():
    try:
        accessToken = request.headers.get('Access-Token')
        whitelist = request.json['whitelist']
        prefList = request.json['prefList']
        userResponse = getUser(accessToken)
        if 'error' in userResponse:
            return userResponse
        userEmail = userResponse['userPrincipalName']
        currUser = colUsers.find_one({'email': userEmail})
        userId = currUser['_id']
        currPref = colPref.update_one({'userId': userId}, {'$set': {'prefList': prefList, 'whitelist': whitelist}}, upsert=True)
        for pref in prefList:
            logic.regUser(str(userId))
            logic.userNLR(pref)
        for wl in whitelist:
            logic.regUser(str(userId))
            logic.addToWhiteList(wl)
        return {'error': False}
    except Exception as e:
        return {'error': True, 'message': e}
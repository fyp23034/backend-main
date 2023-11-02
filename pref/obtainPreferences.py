from pref import client

db = client.fyp
colUsers = db.users
colPref = db.userPreferences

def obtainPreferences(userEmail):
    currUser = colUsers.find_one({'email': userEmail})
    userId = currUser['_id']
    currPref = colPref.find_one({'userId': userId})
    if not currPref:
        currPref = {
            'userId': userId,
            'prefList': [],
            'whitelist': []
        }
        colPref.insert_one(currPref)
    return currPref
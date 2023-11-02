import requests

def getUser(accessToken):
    userEndpoint = "https://graph.microsoft.com/v1.0/me"
    headers = {"Authorization": f"Bearer {accessToken}"}
    userResponse = requests.get(userEndpoint,headers=headers).json()
    if 'error' in userResponse:
        return {'error': True, 'message': 'Invalid access token'}
    return userResponse
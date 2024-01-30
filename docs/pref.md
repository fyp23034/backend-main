# Documentation for /pref API routes

## http://127.0.0.1:5000/pref/getPreferences
This endpoint sends an HTTP GET request to retrieve preferences from the server.
The response will have a status code of 200 and a content type of application/json. The response body will contain an "error" boolean field, along with "prefList" and "whitelist" arrays. The "prefList" array contains the preferences, and the "whitelist" array contains whitelisted items.
Please refer to the API documentation for more details on the structure and usage of the response data.
### Request
- Method: **GET**
#### Request Headers
- Content-Type: application/json
- Access-Token: [Obtained from MSAL]
### Response
- Status: 200
- Content-Type: application/json
#### Response Body
- `error` (boolean): Indicates if an error occurred.
- `prefList` (array of strings): User's preferences
- `whitelist` (array of strings): User's whitelist

## http://127.0.0.1:5000/pref/updatePreferences
This endpoint is used to update user preferences. The HTTP POST request should be sent to [http://127.0.0.1:5000/pref/updatePreferences](http://127.0.0.1:5000/pref/updatePreferences) with a JSON payload in the raw request body type. The payload should include "whitelist" and "prefList" keys.
### Request
- Method: **POST**
#### Request Headers
- Content-Type: application/json
- Access-Token: [Obtained from MSAL]
#### Request Body
- `whitelist` (array of strings): User's updated whitelist
- `prefList` (array of strings): User's updated preference list
### Response
Upon a successful execution, the endpoint returns a JSON response with a status code of 200 and a Content-Type of application/json. The response body contains an "error" key, which is a boolean value indicating whether an error occurred during the update.

Example:

``` json
{
    "error": true
}

 ```
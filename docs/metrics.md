# Documentation for /metrics API routes

## http://127.0.0.1:5000/metrics/recordClick/{id}
This endpoint allows you to record a click for a specific email. Upon making a POST request to the specified URL, the server will respond with a JSON object containing an "error" key, which indicates whether the operation was successful or not.
### Request
- Method: **POST**
#### Request Headers
- Content-Type: application/json
- Access-Token: [Optional for this route]
### Response
- Status: 200
- Content-Type: application/json
#### Response Body
- `error` (boolean): Indicates if an error occurred.

## http://127.0.0.1:5000/metrics/recordTime/{id}
This endpoint allows you to update the time spent for a specific email.
### Request
- Method: **POST**
#### Request Headers
- Content-Type: application/json
- Access-Token: [Optional for this route]
#### Request Body
- timeSpent (number, required): The time spent on the metric in epoch time.
### Response
- Status: 200
- Content-Type: application/json
#### Response Body
- `error` (boolean): Indicates whether an error occurred during the request.
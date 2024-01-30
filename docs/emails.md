# Documentation for /emails API routes

## http://127.0.0.1:5000/emails?page={pageNum}

This endpoint makes an HTTP GET request to retrieve a list of emails, with an optional query parameter for pagination. The response will contain an array of email objects, along with an error flag and the total number of emails available.

### Request Details

- Method: **GET**
- Query Parameters:
    - page: The page number for pagination

#### Request Headers

- Content-Type: application/json
- Access-Token: [Obtained from MSAL]

### Response

- Status: 200
- Content-Type: application/json
- Body:
    
    ``` json
    {
        "emails": [
            {
                "bodyPreview": "",
                "id": "",
                "sender": {
                    "address": "",
                    "name": ""
                },
                "subject": "",
                "time": ""
            }
        ],
        "error": true / false,
        "totalEmails": 0
    }
    
     ```

## http://127.0.0.1:5000/emails/{id}

This endpoint retrieves the details of a specific email. 
The response will have a status code of 200 and a content type of application/json. The response body will contain an "email" object with "bcc", "body", "cc", "sender", and "subject" fields. The "sender" field will have "address" and "name" subfields. 
In addition, the response will include an "error" field indicating whether there was an error in processing the request.

### Request

- Method: **GET**

#### Request Headers

- Content-Type: application/json
- Access-Token: [Obtained from MSAL]

### Response

- Status: 200
- Content-Type: application/json

#### Response body:

- Body:
    
    ``` json
    {
        "emails": {
            {
                "bcc": [""],
                "body": [""],
                "cc": [""],
                "sender": {
                    "address": "",
                    "name": ""
                },
                "subject": "",
            }
        },
        "error": true / false,
    }
    
     ```

## http://127.0.0.1:5000/emails/getByCategory?page={pageNum}&category={category}

This endpoint makes an HTTP GET request to retrieve emails based on a specified category and page number. The request should include the 'page' parameter for pagination and the 'category' parameter to filter emails by category.

### Request

- Method: **GET**

#### Request Headers

- Content-Type: application/json
- Access-Token: [Optional for this route]

#### Request Parameters

- page: (number) The page number for pagination.
- category: (string) The category to filter the emails. Can be either: Low Importance, Mid Importance, High Importance [**NOT FINALIZED!!!**]

Example: [http://127.0.0.1:5000/emails/getByCategory?page=1&category=High Importance]()
    
### Response

- Status: 200
- Content-Type: application/json
    
#### Response Body

Upon a successful request, the server returns a JSON object with the following properties:

Example:

``` json
{
    "emails": [
        {
            "bodyPreview": "",
            "id": "",
            "sender": {
                "address": "",
                "name": ""
            },
            "subject": "",
            "time": ""
        }
    ],
    "error": true,
    "totalEmails": 0
}

 ```

- emails: An array of email objects.
- error: A boolean indicating if an error occurred.
- totalEmails: The total number of emails returned.
    
## http://127.0.0.1:5000/emails/changeCategory/{id}

This endpoint is used to change the category of an email. The HTTP POST request is sent to the specified URL with the email's unique identifier and the new category as part of the request payload.

### Request

- Method: **POST**
- Content-Type: application/json
- Access-Token: [Optional for this route]

#### Request Body
- newCategory (string, required): The new category to be assigned to the email.  

### Response

Upon a successful execution, the endpoint returns a JSON object with a status code of 200 and the content type as application/json. The response body contains an "error" key, which is a boolean indicating whether the operation was successful or not.

Example:

``` json
{
    "error": true / false
}

 ```

## http://127.0.0.1:5000/emails/getSummary/{id}

This endpoint retrieves the summary for a specific email identified by its unique ID.

### Request

#### Request Details

- Method: **GET**

#### Request Headers

- Content-Type: application/json
- Access-Token: [Optional for this route]

### Response

- Status: 200
- Content-Type: application/json
    
#### Response Body

- `error` (boolean): Indicates if an error occurred.
- `summary` (string): The summary of the email.

If `error` is False, `message` will be returned rather than `summary`
from unittest.mock import patch

@patch('requests.get')
def test_get_emails(mock_get_outlook, client):
    mock_get_outlook.return_value.json.return_value = {
        "@odata.context": "https://graph.microsoft.com/v1.0/$metadata#users('fyp23034%40outlook.com')/messages",
        "values": [
            {
                "@odata.etag": "W/\"CQAAABYAAACoOtHbvNh2QL178DUPXHYnAAAAAAkA\"",
                "id": "AQMkADAwATM0MDAAMS02MjE1LTNmMjktMDACLTAwCgBGAAADdkF5WQ88-UKgjxDnLe5RlQcAqDrR27zYdkC9e-A1D1x2JwAAAgEMAAAAqDrR27zYdkC9e-A1D1x2JwAAAg0pAAAA",
                "createdDateTime": "2023-10-05T07:34:54Z",
                "lastModifiedDateTime": "2023-10-05T07:35:01Z",
                "changeKey": "CQAAABYAAACoOtHbvNh2QL178DUPXHYnAAAAAAkA",
                "categories": [],
                "receivedDateTime": "2023-10-05T07:34:54Z",
                "sentDateTime": "2023-10-05T07:34:46Z",
                "internetMessageId": "<f3566333-9e5e-4840-b1aa-0aa914b16412@az.centralus.microsoft.com>",
                "subject": "Welcome to your Azure free account",
                "bodyPreview": "Get started with free amounts of services and USD200 credit.\r\n\r\nGo to the portal >\r\n        You have 30 days left to use your credit. Check your remaining credit >\r\nWelcome to Azure, FYP\r\n\r\nBuild your next idea with 12 months of free services and a USD200",
                "importance": "normal",
                "parentFolderId": "AQMkADAwATM0MDAAMS02MjE1LTNmMjktMDACLTAwCgAuAAADdkF5WQ88-UKgjxDnLe5RlQEAqDrR27zYdkC9e-A1D1x2JwAAAgEMAAAA",
                "conversationId": "AQQkADAwATM0MDAAMS02MjE1LTNmMjktMDACLTAwCgAQAH9NrMgijJxPt7WAWtxUPB0=",
                "conversationIndex": "AQHZ915uf02syCKMnE+3tYBa3FQ8HQ==",
                "webLink": "https://outlook.live.com/owa/?ItemID=AQMkADAwATM0MDAAMS02MjE1LTNmMjktMDACLTAwCgBGAAADdkF5WQ88%2FUKgjxDnLe5RlQcAqDrR27zYdkC9e%2FA1D1x2JwAAAgEMAAAAqDrR27zYdkC9e%2FA1D1x2JwAAAg0pAAAA&exvsurl=1&viewmodel=ReadMessageItem",
                "inferenceClassification": "focused",
                "body": {
                    "contentType": "text",
                    "content": "hi"
                },
                "sender": {
                    "emailAddress": {
                        "name": "Microsoft Azure",
                        "address": "azure-noreply@microsoft.com"
                    }
                },
                "from": {
                    "emailAddress": {
                        "name": "Microsoft Azure",
                        "address": "azure-noreply@microsoft.com"
                    }
                },
                "toRecipients": [
                    {
                        "emailAddress": {
                            "name": "fyp23034@outlook.com",
                            "address": "fyp23034@outlook.com"
                        }
                    }
                ],
                "ccRecipients": [],
                "bccRecipients": [],
                "replyTo": [],
                "flag": {
                    "flagStatus": "notFlagged"
                }
            }
        ]
    }
    response = client.get('/emails')
    # TODO
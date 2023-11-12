from unittest.mock import patch, Mock

# # @patch('requests.get')
# def test_get_emails(client):
#     # mock_response = Mock()
#     # mock_response.json.return_value = {
#     #     "values": [
#     #         {
#     #             "id": "id-test",
#     #             "receivedDateTime": "2023-10-05T07:34:54Z",
#     #             "internetMessageId": "<f3566333-9e5e-4840-b1aa-0aa914b16412@az.centralus.microsoft.com>",
#     #             "subject": "subject-test",
#     #             "bodyPreview": "bodyPreview-test",
#     #             "body": {
#     #                 "contentType": "text",
#     #                 "content": "hi"
#     #             },
#     #             "sender": {
#     #                 "emailAddress": {
#     #                     "name": "sender-test",
#     #                     "address": "sender-address-test"
#     #                 }
#     #             },
#     #             "from": {
#     #                 "emailAddress": {
#     #                     "name": "sender-test",
#     #                     "address": "sender-address-test"
#     #                 }
#     #             },
#     #             "toRecipients": [
#     #                 {
#     #                     "emailAddress": {
#     #                         "name": "fyp23034@outlook.com",
#     #                         "address": "fyp23034@outlook.com"
#     #                     }
#     #                 }
#     #             ],
#     #             "ccRecipients": [],
#     #             "bccRecipients": []
#     #         }
#     #     ]
#     # }
#     # mock_get_outlook.return_value = mock_response
#     response = client.get('/emails?page=1', headers = {'Access-Token': 'test-access-token', 'Content-Type': 'application/json'})
#     # mock_get_outlook.assert_called_once()
#     print(response)
#     data = response.get_json()
#     assert data['error'] == False
#     assert data['emails'][0]['subject'] == 'subject-test'
#     assert data['emails'][0]['bodyPreview'] == 'bodyPreview-test'
#     assert data['emails'][0]['id'] == 'id-test'
#     assert data['emails'][0]['sender'] == { 'name': 'sender-test', 'address': 'sender-address-test' }
#     assert data['emails'][0]['time'] == '2023-10-05T07:34:54Z'

def test_get_by_category(client):
    response = client.get('/emails/getByCategory?page=1&category=', headers = {'Content-Type': 'application/json', 'Access-Token': 'test'})
    data = response.get_json()
    assert data['error'] == False
    assert data['emails']
    assert 'message' not in data
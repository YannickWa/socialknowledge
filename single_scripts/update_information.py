# 'import requests

# #def update_confluence_content(page_id):
# confluence_base_url = 'https://socialknowledge.atlassian.net/wiki/rest/api'

# page_id = 2523156
# # URL for the Confluence REST API to update content
# update_url = f'{confluence_base_url}/content/{page_id}'

# # Updated content data
# updated_content = {
#     "version": {
#         "number": 4  
#     },
#     "id": page_id,
#     "title": "KI Chatbots 2",
#     "type": "page",
#     "body": {
#         "storage": {
#             "value": "Geht das nicht oder wie?",
#             "representation": "storage"
#         }
#     }
# }

headers = {
    'Content-Type': 'application/json',
    "Authorization": "Basic dml0YWxpLnJlaW5oYXJkdDAwN0BnbWFpbC5jb206QVRBVFQzeEZmR0YwNmhabFdwN2g4aTh2MHFkaVU2VkJYR3BaN1RBYmJHbE4yTzJyZjhpWEN2TEN3STFHaWlzeHlwMEE1cEM1RzR3amdiYl93ZWlUcTZ2Nmtwb2ZlbmliUXFqOHJZa2NFOEdyVkNqb1o3Q2syYmdKS0RNdS1qbjRuX00ydFpsRGJfVHh0eDhpTks4TGI4UnRmRDE2WkpqbEM5NEZwTnBMOGFta3VlYUhBMjEzTWNRPTgzMTUxNEZC"
}

# # Make the request to update content
# response = requests.put(update_url, json=updated_content, headers=headers)

# print(f"Request URL: {response.request.url}")
# print(f"Request Headers: {response.request.headers}")
# print(f"Request Body: {response.request.body}")
# print(f"Response Status Code: {response.status_code}")
# print(f"Response Text: {response.text}")

# if response.status_code == 200:
#     print('Content updated successfully')
# else:
#     print(f'Failed to update content. Status code: {response.status_code}')

# # Replace 123456 with the actual page ID you want to update
# #update_confluence_content(2523156)
import requests

confluence_base_url = 'https://socialknowledge.atlassian.net/wiki/rest/api'
page_id = 2523156

# Step 1: Retrieve current content
get_url = f'{confluence_base_url}/content/{page_id}?expand=body.storage,version'
response = requests.get(get_url, headers=headers)

if response.status_code != 200:
    print(f'Failed to retrieve current content. Status code: {response.status_code}')
    exit()

current_content = response.json()
current_version = current_content['version']['number']
existing_content = current_content['body']['storage']['value']
current_title = current_content["title"]

# Step 2: Concatenate existing content with new content
new_content_to_add = "Das klappt ja sogar!"
combined_content = existing_content + f"<p>{new_content_to_add}</p>"

# Step 3: Update page with combined content
update_url = f'{confluence_base_url}/content/{page_id}'
updated_content = {
    "version": {
        "number": current_version + 1  # Increment version number
    },
    "title": current_title,
    "type": "page",
    "body": {
        "storage": {
            "value": combined_content,
            "representation": "storage"
        }
    }
}

# Step 4: Make the request to update content
response = requests.put(update_url, json=updated_content, headers=headers)

if response.status_code == 200:
    print('Content updated successfully')
else:
    print(f'Failed to update content. Status code: {response.text}')
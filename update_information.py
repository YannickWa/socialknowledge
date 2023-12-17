import requests
from http import JsonResponse
import secret

def update_confluence_content(request, page_id):
    confluence_base_url = 'https://socialknowledge.atlassian.net/wiki/rest/api'

    # URL for the Confluence REST API to update content
    update_url = f'{confluence_base_url}/content/{page_id}'

    # Updated content data
    updated_content = {
        "version": {
            "number": 2  
        },
        "title": "Updated Title",
        "type": "page",
        "body": {
            "storage": {
                "value": "<p>Your updated content goes here.</p>",
                "representation": "storage"
            }
        }
    }

    headers = {
        'Content-Type': 'application/json',
        "Authorization": f"Basic {secret.APIKEY_confluence}"
    }

    # Make the request to update content
    response = requests.put(update_url, json=updated_content, headers=headers)

    if response.status_code == 200:
        return JsonResponse({'message': 'Content updated successfully'})
    else:
        return JsonResponse({'error': f'Failed to update content. Status code: {response.status_code}'}, status=500)
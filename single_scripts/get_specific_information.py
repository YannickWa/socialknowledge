import requests
import secret

def get_confluence_page_content(page_id, confluence_base_url, headers):
    # URL for the Confluence REST API to get content
    get_page_url = f'{confluence_base_url}/content/{page_id}?expand=body.view'

    # Headers for authentication
    headers = {
        'Content-Type': 'application/json',
        "Authorization": f"Basic {secret.APIKEY_confluence}"
    }

    # Make the request to get page content
    response = requests.get(get_page_url, headers=headers)

    if response.status_code == 200:
        # Extract content from the response JSON
        content = response.json().get('body', {}).get('view', {}).get('value', '')
        return content
    else:
        print(f'Failed to get content. Status code: {response.status_code}')
        return None
if __name__ == "__main__":
    # Replace these values with your Confluence credentials and configuration
    your_confluence_base_url = 'https://socialknowledge.atlassian.net/wiki/rest/api'
    your_page_id = 2523156 
    headers = {
        'Content-Type': 'application/json',
        "Authorization": f"Basic {secret.APIKEY_confluence}"
    }
    # Fetch content from Confluence page
    page_content = get_confluence_page_content(your_page_id, your_confluence_base_url, headers)

    if page_content is not None:
        print("Confluence Page Content:")
        print(page_content)

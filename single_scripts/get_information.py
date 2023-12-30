import requests
import secret

# Replace the following with your actual values
confluence_url = "https://socialknowledge.atlassian.net/wiki"
space_key = "Documentat"
api_url = f"{confluence_url}/rest/api/space/{space_key}/content"

# Set the authentication headers if required
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Basic {secret.APIKEY_confluence}"
}

# Make the GET request to retrieve space information
response = requests.get(api_url, headers=headers)

# Check the response status
if response.status_code == 200:
    space_info = response.json()
    #print(space_info["page"]["results"][0]["id"])
    #print(space_info["page"]["results"])
    #print(space_info["page"])
    print(space_info["page"])["results"]["_expandable"]
    
    #print(space_info["page"]["results"]["title"])
else:
    print(f"Failed to retrieve space information. Status code: {response.status_code}")
    print("Error response:", response.text)
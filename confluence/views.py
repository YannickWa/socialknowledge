from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
import requests
import os
from django.conf import settings
from .forms import UploadFileForm
from .utils import extract_text_from_word, extract_text_from_text_file
import openai
import secret

# Set your OpenAI API key
openai.api_key = secret.APIKEY_openAI

### Mui Importante: Prompt ###
def openai_process_content(content):
    response = openai.ChatCompletion.create(
        model="gpt-4-1106-preview",
        messages=[
            {"role": "system", "content": "Als textuellen Input kriegst du Notizen oder Stichpunkte die du inhaltlich zusammenfasst. \
            \ Der Output sollte so aufbereitet werden, dass er auf einer Knowledge-Sharing Plattform landet und gegebenenen Konventionen entspricht. \
             Wende dafür entsprechende Confluence Syntax und Markup-Formattierungen an, um den Text aufzubereiten. Benutze falls angebracht Elemente wie Iframes oder Tabellen."},
            {"role": "user", "content": f"Folgenden Inhalt zusammenfassen und formatieren: '{content}'"},
        ],
        max_tokens=700,
    )
    return response.choices[0].message["content"]

### Dateien Upload ###
### Noch in der Beta ###
def handle_uploaded_file(file):
    file_path = os.path.join(settings.BASE_DIR, file.name)
    with open(file_path, 'wb+') as destination:
        for chunk in file.chunks():
            destination.write(chunk)
    return file_path

### Noch in der Beta ###
def extract_text(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded_file = request.FILES['file']
            file_path = handle_uploaded_file(uploaded_file)

            # Determine the file type and extract text accordingly
            if file_path.endswith('.docx'):
                text_content = extract_text_from_word(file_path)
            elif file_path.endswith('.txt'):
                text_content = extract_text_from_text_file(file_path)
            else:
                text_content = "Unsupported file type"

            return render(request, 'extracted_text.html', {'text_content': text_content})

    else:
        form = UploadFileForm()

    return render(request, 'upload_file.html', {'form': form})

### Confluence - Create new Page ###
def modify_content(request):
    if request.method == 'POST':
        space_key = request.POST.get('space', '')
        
        # Map the selected space to the corresponding space_key
        space_key_mapping = {
            'Space1': 'TEAM',
            'Space2': 'Documentat',
        }

        # Get the space_key based on the user's selection
        space_key = space_key_mapping.get(space_key, '')

        title = request.POST.get('title', '')
        content = request.POST.get('content', '')

        # Check if there's an uploaded file
        if 'file' in request.FILES:
            uploaded_file = request.FILES['file']
            file_path = handle_uploaded_file(uploaded_file)

            # Determine the file type and extract text accordingly
            if file_path.endswith('.docx'):
                text_content_from_file = extract_text_from_word(file_path)
            elif file_path.endswith('.txt'):
                text_content_from_file = extract_text_from_text_file(file_path)
            else:
                text_content_from_file = "Unsupported file type"

            # Prioritize pasted content if both are present
            if content.strip() == '':
                content = text_content_from_file

        # Process content using OpenAI API
        processed_content = openai_process_content(content)

        data = {
            "type": "page",
            "title": title,
            "body": {
                "storage": {
                    "value": processed_content,
                    "representation": "wiki",
                }
            },
            "space": {"key": space_key},
        }

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Basic {secret.APIKEY_confluence}"
        }

        # Make the API request
        response = requests.post('https://socialknowledge.atlassian.net/wiki/rest/api/content', json=data, headers=headers)

        # Check the response - new
        if response.status_code == 200:
            page_url = response.json().get('_links', {}).get('webui', '')
            success_message = f"Page created or updated successfully. Page URL: {page_url}"

            # Get the processed content from the API response
            processed_content = response.json().get('body', {}).get('storage', {}).get('value', '')

            return render(
                request,
                'result_template.html',
                {'success_message': success_message, 'page_url': page_url, 'processed_content': processed_content}
            )
        else:
            error_message = f"Failed with status code {response.status_code}: {response.text}"
            return render(request, 'result_template.html', {'error_message': error_message})

    return render(request, 'modify_content.html')


### Confluence - Get Space and Page Info ###
def confluence_space_info(request):
    if request.method == 'POST':
        # Retrieve the space key from the form submission
        space_key = request.POST.get('space_key', '')
        
        # Replace the following with your actual values
        confluence_url = "https://socialknowledge.atlassian.net/wiki"
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
            result = response.json()
            space_info = result["page"]["results"]
            return render(request, 'confluence_space_info.html', {'space_info': space_info, 'space_key': space_key})
        else:
            error_message = f"Failed to retrieve space information. Status code: {response.status_code}"
            return render(request, 'error_template.html', {'error_message': error_message})
        
    return render(request, 'space_input_form.html')

### Multi-Step Posting auf ausgewählten Confluence-Bereich ###

def step_1(request):
    if request.method == 'POST':
        space_key = request.POST.get('space', '')
        title = request.POST.get('title', '')
        input_text = request.POST.get('input_text', '')

        # Map the selected space to the corresponding space_key
        space_key_mapping = {
            'Space1': 'TEAM',
            'Space2': 'Documentat',
        }

        # Get the space_key based on the user's selection
        space_key = space_key_mapping.get(space_key, '')

        # Check if there's an uploaded file
        if 'file' in request.FILES:
            uploaded_file = request.FILES['file']
            file_path = handle_uploaded_file(uploaded_file)

            # Determine the file type and extract text accordingly
            if file_path.endswith('.docx'):
                text_content_from_file = extract_text_from_word(file_path)
            elif file_path.endswith('.txt'):
                text_content_from_file = extract_text_from_text_file(file_path)
            else:
                text_content_from_file = "Unsupported file type"

            # Prioritize pasted content if both are present
            if input_text.strip() == '':
                input_text = text_content_from_file

        processed_content = openai_process_content(input_text)
        return render(request, 'step2.html', {'input_text': input_text, 'processed_content': processed_content, 'space_key': space_key, 'title': title})
    return render(request, 'step1.html', {'input_text': '', 'processed_content': '', 'space_key': '', 'title': ''})

def step_2(request):
    if request.method == 'POST':
        #Get the space_key based on the user's selection
        space_key = request.POST.get('space', '')
        title = request.POST.get('title', '')
        processed_content = request.POST.get('processed_content', '')

        # Your logic for making the API request to update content
        data = {
            "type": "page",
            "title": title,
            "body": {
                "storage": {
                    "value": processed_content,
                    "representation": "wiki",
                }
            },
            "space": {"key": space_key},
        }

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Basic {secret.APIKEY_confluence}"
        }

        response = requests.post('https://socialknowledge.atlassian.net/wiki/rest/api/content', json=data, headers=headers)
        
        
        # Check the response
        if response.status_code == 200:
            page_url = response.json().get('_links', {}).get('webui', '')
            success_message = f"Page created or updated successfully. Page URL: {page_url}"

            # Get the processed content from the API response
            processed_content = response.json().get('body', {}).get('storage', {}).get('value', '')

            return render(
                request,
                'step3.html',
                {'success_message': success_message, 'page_url': page_url, 'processed_content': processed_content}
            )
        else:
            error_message = f"Error in Confluence API request. Status code: {response.status_code} {space_key} {title}"
            return render(request, 'error_template.html', {'error_message': error_message})

    return render(request, 'step2.html')

def step_3(request):
    # Additional logic for the final step if needed
    # ...
    return render(request, 'step3.html')

def index(request):
    return render(request, 'index.html')

### Confluence Update Content - Testing ### 
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
from django.shortcuts import render
from django.http import HttpResponse
import requests
import os
from django.conf import settings
from .forms import UploadFileForm
from .utils import extract_text_from_word, extract_text_from_text_file
import openai
import secret

# Set your OpenAI API key
openai.api_key = secret.APIKEY_openAI

def handle_uploaded_file(file):
    file_path = os.path.join(settings.BASE_DIR, file.name)
    with open(file_path, 'wb+') as destination:
        for chunk in file.chunks():
            destination.write(chunk)
    return file_path

def openai_process_content(content):
    response = openai.ChatCompletion.create(
        model="gpt-4-1106-preview",
        messages=[
            {"role": "system", "content": "Du bist ein System das bei Knowledge-Sharing hilft. Als Input erhälst du kurze Notizen zu spezifischen Themenfeldern. Bitte nehme diese Notizen und erstelle daraus schönen Fließtext ohne den Inhaltsgehalt zu verändern."},
            {"role": "user", "content": f"Folgenden Inhalt zusammenfassen und formatieren: '{content}'"},
        ],
        max_tokens=500,
    )
    return response.choices[0].message["content"]

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

def modify_content(request):
    if request.method == 'POST':
        space_key = request.POST.get('space', '')
        
        # Map the selected space to the corresponding space_key
        space_key_mapping = {
            'Space1': 'TEAM',
            'Space2': 'Documentat',
            # Add more mappings as needed
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

        #cleaned_content = content = content.replace('<', '&lt;').replace('>', '&gt;')

        # Process content using OpenAI API
        processed_content = openai_process_content(content)

        # Construct the data payload
        data = {
            "type": "page",
            "title": title,
            "body": {
                "storage": {
                    "value": processed_content,
                    "representation": "storage",
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

        # Check the response
        if response.status_code == 200:
            return HttpResponse(f"Page created or updated successfully. Page URL: {response.json()['_links']['webui']}")
        else:
            return HttpResponse(f"Failed with status code {response.status_code}: {response.text}")

    return render(request, 'modify_content.html')

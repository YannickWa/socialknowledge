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
openai.api_key =  secret.APIKEY_openAI

# ### Mui Importante: Prompt ###
# def openai_process_content(content):
#     response = openai.ChatCompletion.create(
#         model="gpt-4-1106-preview",
#         messages=[
#             {"role": "system", "content": "Als textuellen Input kriegst du Notizen oder Stichpunkte die du inhaltlich zusammenfasst. \
#             \ Der Output sollte so aufbereitet werden, dass er auf einer Knowledge-Sharing Plattform landet und gegebenenen Konventionen entspricht. \
#              \ Wende dafür entsprechende Confluence Syntax und Markup-Formattierungen an, um den Text aufzubereiten. Benutze falls angebracht Elemente wie Iframes oder Tabellen. \
#              \ Eingefügte Links und Bilder verweisen nicht auf entsprechende Confluence Inhalte sondern sind entsprechend darzustellen. Vorhandene Codeschnipsel bitte formattiert darstellen."},
#             {"role": "user", "content": f"Folgenden Inhalt zusammenfassen und formatieren: '{content}'"},
#         ],
#         max_tokens=1200,
#     )
#     return response.choices[0].message["content"]

### Mui Importante: Prompt ###
# basic_prompt = "Als textuellen Input kriegst du Notizen oder Stichpunkte die du inhaltlich zusammenfasst. \
#              \ Bereite den Output so vor, dass er vorzeigbar auf Confluence landen kann und verwende dafür Confluence-Syntax-Elemente und Markup-Formattierungen. \
#               \ Verzichte auf eine Beschreibung deines Vorhabens und den Hinweisen am Ende. Stelle Links und Bilder so dar wie sie reinkommen, ohne auf Confluence Inhalte zu verweisen."


basic_prompt = "Verfasse einen Confluence-kompatiblen Artikel basierend auf dem folgenden textuellen Inhalt. Der Artikel soll klare Struktur und Confluence-Syntax aufweisen, einschließlich Überschriften, Listen, Links und anderen Formatierungen. Betone wichtige Informationen visuell durch Panels oder Symbole. Beachte dabei, dass der Output direkt auf einer Confluence-Seite veröffentlicht werden soll."


def openai_process_content(content, concatenated_prompt, max_tokens_key):
    response = openai.ChatCompletion.create(
        model="gpt-4-1106-preview",
        messages=[
            {"role": "system", "content": f'{basic_prompt}' + f" '{concatenated_prompt}'."},
            {"role": "user", "content": f"Folgenden textuellen Inhalt zusammenfassen und formatieren: '{content}'"},
        ],
        max_tokens=max_tokens_key,
        temperature = 0.8,
    )
    return response.choices[0].message["content"]

# def openai_update_content(content):
#     response = openai.ChatCompletion.create(
#         model="gpt-4-1106-preview",
#         messages=[
#             {"role": "system", "content": f"'{basic_prompt}'."},
#             {"role": "user", "content": f"Folgenden textuellen Inhalt zusammenfassen und formatieren: '{content}'"},
#         ],
#         max_tokens=500,
#         temperature = 0.8,
#     )
#     return response.choices[0].message["content"]


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
            'Space3': 'YannickTes',
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
            space_info = result.get("page", {}).get("results", [])
            
            # Assuming each page_info dictionary has 'title', 'page_id', 'description', and 'url'
            for page_info in space_info:
                page_title = page_info["title"]
                #space_titles = [page.get("title", "") for page in result.get("page", {}).get("results", [])]
                page_info['url'] = f"{confluence_url}/spaces/{space_key}/pages/{page_info['id']}/{page_title}"

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
        #prompt_key = request.POST.get('prompt')  
        #template = request.POST.get('template', '')
        selected_prompt_keys = request.POST.getlist('prompt')
        max_tokens_key = request.POST.get('max_tokens', '')

        #concatenated_values = ' '.join(prompt_mapping.get(prompt, '') for prompt in prompt_key)

        # Map the selected space to the corresponding space_key
        space_key_mapping = {
            'Space1': 'TEAM',
            'Space2': 'Documentat',
            'Space3': 'YannickTes',
            'Space4': 'VitaliTest',
        }

        prompt_mapping = {
            'Tables': 'Tabellen, für eine bessere Übersicht, ',
            'Codes': 'Codebausteine und Code-Highlighting im "{code}" Format, ',
            'Makros': 'Makros (z.B. Panels, Expand, Notes, etc.), um Inhalte hervorzuheben, ',
            'Symbols': 'Symbole und Icons für eine bessere Darstellung von Zwischenschritten, ',
            # 'Previews': 'Previews, ',
            # 'Interactive': 'Interactive Elements, ',
            # 'Expand': 'Expands, ',
            'Statuses': 'Interaktive Statuselemente ',
        }

        max_tokens_mapping = {
            'Short': 400,
            'Middle': 800,
            'Long': 1200,
        }

        # Get the keys bases on user choice
        space_key = space_key_mapping.get(space_key, '')
        # prompt_key = prompt_mapping.get(prompt_key, '')
        concatenated_prompt = 'Folgende Confluence-Elemente sind in jedem Fall zu verwenden: ' + ' '.join(prompt_mapping.get(prompt, '') for prompt in selected_prompt_keys)
        max_tokens_key = max_tokens_mapping.get(max_tokens_key, '')

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
        
        #print(concatenated_values)
        processed_content = openai_process_content(input_text, concatenated_prompt, max_tokens_key)
        return render(request, 'step2.html', {'input_text': input_text, 'processed_content': processed_content, 'space_key': space_key, 'title': title, 'concatenated_prompt': concatenated_prompt}) #, 'prompt_key': prompt_key, 'template': template, 'max_tokens_key': max_tokens_key
    return render(request, 'step1.html', {'input_text': '', 'processed_content': '', 'space_key': '', 'title': '', 'prompt_key': '', 'template': '', 'max_tokens_key': '', 'concatenated_prompt': ''})

def step_2(request):
    if request.method == 'POST':
        #Get the space_key based on the user's selection
        space_key = request.POST.get('space', '')
        title = request.POST.get('title', '')
        processed_content = request.POST.get('processed_content', '')
        #template = request.POST.get('template', '')

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
            #"template": {"name": template},
        }

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Basic {secret.APIKEY_confluence}"
        }

        response = requests.post('https://socialknowledge.atlassian.net/wiki/rest/api/content', json=data, headers=headers)
        
        prefix = "https://socialknowledge.atlassian.net/wiki"
        
        # Check the response
        if response.status_code == 200:
            page_url = response.json().get('_links', {}).get('webui', '')
            success_message = f"Page wurde erfolgreich angelegt:"

            # Get the processed content from the API response
            processed_content = response.json().get('body', {}).get('storage', {}).get('value', '')

            return render(
                request,
                'step3.html',
                {'success_message': success_message, 'page_url': page_url, 'processed_content': processed_content}
            )
        else:
            error_message = f"Error in Confluence API request. Status code: {response.status_code} {space_key} {title} \
                {response.text}"
            return render(request, 'error_template.html', {'error_message': error_message})

    return render(request, 'step2.html')

def step_3(request):
    # Additional logic for the final step if needed
    # ...
    return render(request, 'step3.html')

def index(request):
    return render(request, 'index.html')

### Confluence Update Content - Testing ### 
def update_confluence_content(request):

    if request.method == 'POST':
        # Retrieve the page_id and update_text from the form submission
        page_id = request.POST.get('page_id', '')
        update_text = request.POST.get('update_text', '')

        # Validate that page_id and update_text are not empty
        if not page_id or not update_text:
            return JsonResponse({'error': 'Invalid form data. Please provide both page_id and update_text.'}, status=400)

        confluence_base_url = 'https://socialknowledge.atlassian.net/wiki/rest/api'

        # Step 1: Retrieve current content
        get_url = f'{confluence_base_url}/content/{page_id}?expand=body.storage,version'
        headers = {
            'Content-Type': 'application/json',
            "Authorization": f"Basic {secret.APIKEY_confluence}"
        }
        response = requests.get(get_url, headers=headers)

        if response.status_code != 200:
            return JsonResponse({'error': f'Failed to retrieve current content. Status code: {response.status_code}'}, status=500)

        current_content = response.json()
        current_version = current_content['version']['number']
        existing_content = current_content['body']['storage']['value']
        current_title = current_content["title"]

        # Step 2: Concatenate existing content with new content
        #new_content_to_add = openai_update_content(update_text)
        new_content_to_add = f"<p>{update_text}</p>"
        combined_content = existing_content + new_content_to_add

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
            return JsonResponse({'message': 'Content updated successfully'})
        else:
            return JsonResponse({'error': f'Failed to update content. Status code: {response.status_code, response.text}'}, status=500)

    return render(request, 'update_confluence_content.html')
Python installieren falls nicht vorhanden
Python Version sollte 3.10+ sein

Empfohlen: Python virtual Environment einrichten und aktivieren

pip bei Bedarf upgraden mit "python -m pip install --upgrade pip"
Django installieren mit: pip install django

Projekt von Yannick Walla (E-Mail: yannick.walla@gmail.com) und Vitali Reinhardt (Tel: 01578 2792454) herunterladen auf https://github.com/YannickWa/socialknowledge

Pip Packages installieren mit: pip install -r requirements.txt

Was wird sonst benötigt?

benötigt wird ebenfalls ein OpenAI-API Key

Anleitung: "https://www.maisieai.com/help/how-to-get-an-openai-api-key-for-chatgpt"

und ein Confluence API-Key "https://support.atlassian.com/atlassian-account/docs/manage-api-tokens-for-your-atlassian-account/"

Was ist Django, wie funktioniert es?
Django Framework erklärt: https://developer.mozilla.org/en-US/docs/Learn/Server-side/Django/Introduction

https://developer.mozilla.org/en-US/docs/Learn/Server-side/Django/Introduction/basic-django.png

Wie benutzt ihr unser Projekt?
OpenAI API-Key und Confluence API-Key in secret.py eintragen

Innerhalb des virtual-environments: navigieren in projektordner "socialknowledge"

python manage.py runserver ausführen

über "http://127.0.0.1:8000/confluence/" die Webpage aufrufen

"Confluence-Content-erschaffen" ==> Bereich und Überschrift auswählen, Token-size und Prompt-Zusätze auswählen, Notizen einfügen per copy paste oder Datei hochladen ==> Process ==> überprüfen, potenziell editieren ==> final auf Confluence hochladen

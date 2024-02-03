# Einrichtung einer Django-Umgebung für das "SocialKnowledge" (Studi-)Projekt

## Zusammenfassung
In diesem Artikel wird beschrieben, wie eine Django-Umgebung für das Arbeiten mit dem "SocialKnowledge" Projekt in Python eingerichtet wird. Schritt-für-Schritt Anleitungen für die Installation von Python, die Einrichtung einer virtuellen Umgebung, das Installieren von Django und anderen erforderlichen Paketen stellen wir hier zur Verfügung, ebenso wie Anleitungen für das Erhalten der notwendigen API-Keys.

## Voraussetzungen
- Python 3.10+ installieren
  - Überprüfen der Python-Version: `python --version`
- Einrichtung einer Python virtuellen Umgebung empfohlen \
  ```python -m venv venv```
- Pip aktualisieren: ```python -m pip install --upgrade pip```
- Django installieren: ```pip install django```

## Projekt Setup (**wichtig!**)
- Projekt herunterladen: \
#Wo wollt ihr das Projekt haben? \
```cd Pfad/Zum/Zielverzeichnis```  \
```git clone https://github.com/YannickWa/socialknowledge``` \
```cd socialknowledge``` \
```git pull origin main``` 
- Erforderliche Pip Packages installieren:
  - ```pip install -r requirements.txt```
- Erforderliche API-Keys:
  - OpenAI-API Key: [Anleitung](https://www.maisieai.com/help/how-to-get-an-openai-api-key-for-chatgpt)
  - Confluence API-Key: [Anleitung](https://support.atlassian.com/atlassian-account/docs/manage-api-tokens-for-your-atlassian-account/)

## Was ist Django?
  <summary>Klicken Sie hier für eine Einführung in Django</summary>
  
  Django ist ein hochgradig skalierbares und flexibles Web-Framework. Für eine tiefere Einführung:
  - [Django Framework - Offizielle Dokumentation](https://developer.mozilla.org/en-US/docs/Learn/Server-side/Django/Introduction)
   ![Django Framework Übersicht](https://developer.mozilla.org/en-US/docs/Learn/Server-side/Django/Introduction/basic-django.png)

  - Falls ihr euch nicht auskennt mit Django, oder generell MVT-Pattern Frameworks empfehlen wir die Doku vorher zu lesen.
## Nutzung des "SocialKnowledge" Projekts
  <summary>Anweisungen zum Start des Projekts</summary>

  - secret_REDACTED.py umbenennen in secret.py
  - API-Keys in `secret.py` eintragen (**wichtig!**)
  - Im virtual-environment, zum Projektordner `socialknowledge` navigieren \
    ```cd ..\socialknowledge\```
  - Ausführen des Servers: ```python manage.py runserver```
  - Die Webpage über [http://127.0.0.1:8000/confluence/](http://127.0.0.1:8000/confluence/) aufrufen

## Erstellen von Inhalten auf Confluence mit unserem Tool
> - Bereich und Überschrift auswählen
> - Token-size und Prompt-Zusätze festlegen
> - Notizen einfügen (per Copy-Paste oder Dateiupload)
> - "Process" klicken zur Verarbeitung
> - Inhalt überprüfen, potenziell bearbeiten
> - Final auf Confluence hochladen



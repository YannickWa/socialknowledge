from docx import Document

def extract_text_from_word(file_path):
    doc = Document(file_path)
    full_text = '\n'.join([paragraph.text for paragraph in doc.paragraphs])
    return full_text

def extract_text_from_text_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        full_text = file.read()
    return full_text
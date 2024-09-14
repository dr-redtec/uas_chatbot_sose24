import sys

def beantworte_frage(text):
    # Erstelle eine statische Antwort, unabhängig vom Eingabetext
    antwort = "Frage wurde beantwortet"
    
    # Den kombinierten Text zurückgeben
    return antwort

import os

def load_md_files(md_folder_path):
    """
    Lädt alle .md-Dateien aus einem angegebenen Ordner und gibt sie als Liste von Dokumenten zurück.

    :param md_folder_path: Der Pfad zum Ordner, der die .md-Dateien enthält.
    :return: Eine Liste mit dem Inhalt aller .md-Dateien.
    """
    documents = []

    # Durchlaufe alle Dateien im angegebenen Ordner
    for filename in os.listdir(md_folder_path):
        # Überprüfen, ob die Datei eine .md-Datei ist
        if filename.endswith('.md'):
            # Vollständigen Pfad zur Datei erstellen
            file_path = os.path.join(md_folder_path, filename)
            # Datei öffnen und Inhalt lesen
            with open(file_path, 'r', encoding='utf-8') as file:
                # Inhalt zur Dokumentenliste hinzufügen
                documents.append(file.read())

    return documents


# Beispiel: Die Funktion aufrufen
md_folder_path = os.path.join('data', 'md')
documents = load_md_files(md_folder_path)


for i, doc in enumerate(documents):
    print(f"Document {i}:\n")
    print(doc)
    print("\n" + "="*50 + "\n")
    
import re
import language_tool_python

# Lade das LanguageTool-Modell für Deutsch
tool = language_tool_python.LanguageTool('de')

# Funktion zur Rechtschreib- und Grammatikprüfung mit LanguageTool
def correct_with_languagetool(text):
    matches = tool.check(text)
    corrected_text = language_tool_python.utils.correct(text, matches)
    return corrected_text

# Korrigieren von gesplitteten Wörtern
def correct_word_splitting(text):
    return re.sub(r'\b(\w+)\s*-\s*(\w+)\b', r'\1\2', text)

# Hauptfunktion zur Bereinigung der Dokumente
def clean_documents(documents):
    cleaned_documents = []
    
    for doc in documents:
        # Entfernen von problematischen Steuerzeichen (z.B. Steuerzeichen, nicht druckbare Zeichen)
        doc = re.sub(r'[\x00-\x1F\x7F]', ' ', doc)  # Entfernt Steuerzeichen
        
        # Sicherstellen, dass keine doppelten Leerzeichen durch das Entfernen von Zeichen entstehen
        doc = re.sub(r'\s+', ' ', doc).strip()
        
        # Korrigieren von gesplitteten Wörtern
        doc = correct_word_splitting(doc)
        
        # Textkorrektur mit LanguageTool
        doc = correct_with_languagetool(doc)
        
        # Bereinigtes Dokument zur Liste hinzufügen
        cleaned_documents.append(doc)
    
    return cleaned_documents

cleaned_documents = clean_documents(documents)

    
for i, doc in enumerate(cleaned_documents):
    print(f"cleaned_documents {i}:\n")
    print(doc)
    print("\n" + "="*50 + "\n")
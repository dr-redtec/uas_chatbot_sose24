import os
from embeddings import *
from llms import *
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import UnstructuredMarkdownLoader
from langchain_core.documents import Document
import numpy as np
import chromadb
from chromadb.config import DEFAULT_TENANT, DEFAULT_DATABASE, Settings
import requests


def delete_chroma_collection(collection_name, persist_directory):
    """
    Löscht eine spezifische Collection aus einer Chroma-Datenbank, falls sie existiert.

    Args:
        collection_name (str): Der Name der Collection, die gelöscht werden soll.
        persist_directory (str): Das Verzeichnis, in dem die Chroma-Datenbank persistiert ist.

    Description:
        Diese Funktion öffnet die Chroma-Datenbank mithilfe eines PersistentClient und überprüft, ob die angegebene Collection existiert.
        Wenn die Collection vorhanden ist, wird sie gelöscht. Falls die Collection nicht existiert, wird eine entsprechende 
        Fehlermeldung ausgegeben.

    Returns:
        None: Gibt keine Rückgabewerte zurück, gibt aber eine Meldung aus, ob die Collection gelöscht wurde oder nicht.
    """
    # Öffne die Chroma-Datenbank mit Persistierung
    client = chromadb.PersistentClient(
        path=persist_directory,
        settings=Settings(),
        tenant=DEFAULT_TENANT,
        database=DEFAULT_DATABASE,
    )
    
    # Überprüfe, ob die Collection existiert, und lösche sie, wenn ja
    existing_collections = [col.name for col in client.list_collections()]
    if collection_name in existing_collections:
        client.delete_collection(name=collection_name)
        print(f"Collection '{collection_name}' erfolgreich gelöscht.")
    else:
        print(f"Collection '{collection_name}' nicht gefunden.")
        
        
def replace_t_with_space(list_of_documents):
    """
    Replaces all tab characters ('\t') with spaces in the page content of each document.

    Args:
        list_of_documents: A list of document objects, each with a 'page_content' attribute.

    Returns:
        The modified list of documents with tab characters replaced by spaces.
    """

    for doc in list_of_documents:
        doc.page_content = doc.page_content.replace('\t', ' ')  # Replace tabs with spaces
    return list_of_documents


def encode_md_from_folder(folder_path, chunk_size, chunk_overlap):
    """
    Lädt alle Markdown-Dateien aus einem Ordner, splittet sie in kleinere Textstücke und bereinigt den Text.

    Args:
        folder_path (str): Der Pfad zum Ordner, der die Markdown-Dateien enthält.
        chunk_size (int): Die maximale Größe eines Textchunks.
        chunk_overlap (int): Die Anzahl der Zeichen, die sich zwischen aufeinanderfolgenden Chunks überlappen.

    Description:
        Diese Funktion durchsucht den angegebenen Ordner nach Markdown-Dateien (.md). Für jede Datei wird der Inhalt mit 
        `UnstructuredMarkdownLoader` geladen und anschließend mit `RecursiveCharacterTextSplitter` in kleinere Chunks aufgeteilt. 
        Die Länge der Chunks wird durch den `chunk_size` bestimmt, und `chunk_overlap` definiert die Anzahl der Zeichen, 
        die in den Chunks überlappen. Nach dem Splitten wird eine Bereinigung durchgeführt, um Tabs durch Leerzeichen zu ersetzen, 
        und die bereinigten Texte werden in einer Liste gesammelt.

    Returns:
        list: Eine Liste der bereinigten Textchunks aus allen Markdown-Dateien im Ordner.
    """
    all_cleaned_texts = []

    # Iterate through all files in the folder
    for filename in os.listdir(folder_path):
        if filename.endswith(".md"):
            file_path = os.path.join(folder_path, filename)

            # Load Markdown documents
            loader = UnstructuredMarkdownLoader(file_path)
            documents = loader.load()

            # Split documents into chunks
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=chunk_size, chunk_overlap=chunk_overlap, length_function=len
            )
            texts = text_splitter.split_documents(documents)
            cleaned_texts = replace_t_with_space(texts)

            # Append cleaned texts to the list
            all_cleaned_texts.extend(cleaned_texts)

    return all_cleaned_texts


def api_to_docs(overpass_url, overpass_query):
    """
    Führt eine Anfrage an die Overpass API durch, verarbeitet die Ergebnisse und erstellt eine Liste von Dokumenten in Markdown-Format.

    Args:
        overpass_url (str): Die URL der Overpass API.
        overpass_query (str): Der Overpass Query, der für die API-Anfrage verwendet wird.

    Description:
        Diese Funktion sendet eine Anfrage an die Overpass API, um Daten über Orte wie Recyclingstationen abzurufen. 
        Die Funktion überprüft die Antwort der API, verarbeitet die Elemente mit relevanten Informationen (wie Name, Adresse, 
        Öffnungszeiten, Telefon, Koordinaten), und erstellt für jedes Element ein Markdown-Dokument. Nur Elemente, die 
        mindestens eine Adresse oder Öffnungszeiten enthalten, werden berücksichtigt. Jedes Dokument enthält den Inhalt im 
        Markdown-Format und kann zusätzliche Metadaten enthalten.

    Returns:
        list: Eine Liste von Dokumenten, die aus den abgerufenen und gefilterten API-Daten erstellt wurden.
    """
    # Anfrage an Overpass API
    response = requests.get(overpass_url, params={'data': overpass_query})

    # Liste der Dokumente
    documents = []
    
    # Überprüfen, ob die Anfrage erfolgreich war
    if response.status_code == 200:
        data = response.json()

        # Ergebnisse auswerten
        for element in data['elements']:
            if 'tags' in element:
                name = element['tags'].get('name', 'Unbenannt')
                address = element['tags'].get('addr:street', 'Keine Adresse verfügbar')
                opening_hours = element['tags'].get('opening_hours', 'Keine Öffnungszeiten verfügbar')
                phone = element['tags'].get('phone', 'Keine Telefonnummer verfügbar')
                lat = element.get('lat', 'Keine Koordinaten')
                lon = element.get('lon', 'Keine Koordinaten')
                
                city = element['tags'].get('addr:city', 'Keine Stadt verfügbar')
                country = element['tags'].get('addr:country', 'Keine Land verfügbar')
                housenumber = element['tags'].get('addr:housenumber', 'Keine Hausnummer verfügbar')
                postcode = element['tags'].get('addr:postcode', 'Keine Postleitzahl verfügbar')
                street = element['tags'].get('addr:street', 'Keine Straße verfügbar')
                suburb = element['tags'].get('addr:suburb', 'Keine Stadtteil verfügbar')

                # Filter: Nur Elemente mit Adresse und Öffnungszeiten
                if address != 'Keine Adresse verfügbar' or opening_hours != 'Keine Öffnungszeiten verfügbar':
                    if name != 'Unbenannt':
                        # Erstelle den Markdown-Text für jede Recyclingstation
                        markdown_text = f"""
                        {name}
                        Stadt: {city}
                        Land: {country}
                        Hausnummer: {housenumber}
                        Postleitzahl: {postcode}
                        Straße: {street}
                        Stadtteil: {suburb}
                        Öffnungszeiten: {opening_hours}
                        Telefon: {phone}
                        Koordinaten: {lat}, {lon}
                        """

                        # Erstelle ein Document-Objekt
                        document = Document(
                            page_content=markdown_text.strip(),  # Der Markdown-Inhalt
                            metadata={  # Optional: Füge Metadaten hinzu, wenn nötig
                                "source": "Overpass API"
                            }
                        )
                        
                        # Füge das Dokument der Liste hinzu
                        documents.append(document)
    return documents

def encode_api(documents, chunk_size, chunk_overlap):
    """
    Teilt eine Liste von Dokumenten in kleinere Textstücke auf und bereinigt den Text.

    Args:
        documents (list): Eine Liste von Dokumenten, die aufgeteilt und bereinigt werden sollen.
        chunk_size (int): Die maximale Größe eines Textchunks.
        chunk_overlap (int): Die Anzahl der Zeichen, die sich zwischen aufeinanderfolgenden Chunks überlappen.

    Description:
        Diese Funktion verwendet `RecursiveCharacterTextSplitter`, um die übergebenen Dokumente in kleinere Chunks 
        zu zerlegen. Die Länge der Chunks wird durch den `chunk_size` bestimmt, und `chunk_overlap` definiert die 
        Anzahl der Zeichen, die sich überlappen. Anschließend wird eine Bereinigung der Texte durchgeführt, um 
        Tabs durch Leerzeichen zu ersetzen. Optional könnte der Inhalt und die Quelle der Dokumente angezeigt werden 
        (auskommentiert in der aktuellen Version).

    Returns:
        list: Eine Liste der bereinigten Textchunks aus den übergebenen Dokumenten.
    """
    # Split documents into chunks
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size, chunk_overlap=chunk_overlap, length_function=len
    )
    texts = text_splitter.split_documents(documents)
    cleaned_texts = replace_t_with_space(texts)

    
    # Gliederung der Dokumente
    # for document in cleaned_texts:
    #     print(f"Quelle: {document.metadata['source']}")
    #     print("\nInhalt:")
    #     print(document.page_content)
    #     print("\n" + "-"*50 + "\n")
    
    return cleaned_texts

def add_embeddings(list_of_documents):
    """
    Fügt Embeddings zu einer Liste von Dokumenten hinzu und speichert diese zusammen mit den Metadaten und dem Inhalt.

    Args:
        list_of_documents (list): Eine Liste von Dokumenten, deren Inhalt mit Embeddings versehen werden soll.
        
    Description:
        Diese Funktion durchläuft die übergebene Liste von Dokumenten. Für jedes Dokument wird mit der Funktion `create_embeddings()` 
        ein Embedding des Inhalts (page_content) generiert. Das Dokument, seine Metadaten und das generierte Embedding werden in einem 
        Dictionary gespeichert und zu einer neuen Liste hinzugefügt. Am Ende wird die Liste von Dictionaries zurückgegeben, 
        wobei jedes Dictionary ein Dokument mit Metadaten, Inhalt und Embeddings enthält.

    Returns:
        list: Eine Liste von Dictionaries, die Metadaten, den Seiteninhalt und die entsprechenden Embeddings der Dokumente enthalten.
    """
    docs_with_embeddings_2 = []
    
    for doc in list_of_documents:
        
        # Generate embeddings for the page content
        embeddings = create_embeddings(doc.page_content)

        # Store the document and its embeddings in a dictionary
        doc_dict = {'metadata': doc.metadata ,'page_content': doc.page_content, 'embeddings': embeddings}
        docs_with_embeddings_2.append(doc_dict)
    
    return docs_with_embeddings_2

def create_chroma_v2(documents, collection_name, persist_directory):
    """
    Erstellt oder öffnet eine Chroma-Datenbank und fügt Dokumente mit Metadaten und Embeddings hinzu.

    Args:
        documents (list): Eine Liste von Dokumenten, die hinzugefügt werden sollen. Jedes Dokument enthält Metadaten, 
                          Seiteninhalt und Embeddings.
        collection_name (str): Der Name der Collection in der Chroma-Datenbank.
        persist_directory (str): Das Verzeichnis, in dem die Chroma-Datenbank gespeichert wird.

    Description:
        Diese Funktion öffnet oder erstellt eine neue Chroma-Datenbank mit Persistierung. Für jedes Dokument in der 
        übergebenen `documents`-Liste wird eine eindeutige ID erzeugt, und die Embeddings sowie Metadaten werden in der 
        Chroma-Collection gespeichert. Jedes Dokument wird als Seiteninhalt zusammen mit den zugehörigen Embeddings und 
        Metadaten (wie die Quelle) hinzugefügt. Falls die Embeddings als NumPy-Array vorliegen, werden sie in Listen umgewandelt.
        Es wird sichergestellt, dass der Seiteninhalt als String vorliegt, bevor er zur Datenbank hinzugefügt wird.

    Returns:
        None: Die Funktion gibt nichts zurück, gibt aber Statusmeldungen aus, wenn Dokumente erfolgreich hinzugefügt wurden.
    """
    # Erstelle oder öffne eine Chroma-Datenbank mit Persistierung
    client = chromadb.PersistentClient(
        path=persist_directory,
        settings=Settings(),
        tenant=DEFAULT_TENANT,
        database=DEFAULT_DATABASE,
    )
    # Erstelle eine neue Collection in der Datenbank oder lade eine bestehende
    collection = client.get_or_create_collection(name=collection_name)
    
    print(f"Chroma-Datenbank '{collection_name}' erfolgreich erstellt.")

    for i, chunk in enumerate(documents):
        # IDs werden dynamisch erzeugt, z.B. basierend auf dem Index
        doc_id = f"id_{i+1}"

        # Konvertiere die Embeddings in eine Liste von Listen
            # Extrahiere die Metadaten, den Seiteninhalt und die Embeddings aus dem Dokument
        source = chunk['metadata']['source']
        page_content = chunk['page_content']
        embeddings = chunk['embeddings']
        
        # Sicherstellen, dass Embeddings in der richtigen Form vorliegen (z.B. Liste von Listen)
        if isinstance(embeddings, np.ndarray):  # Falls die Embeddings als NumPy-Array vorliegen
            embeddings = embeddings.tolist()
            
        # Sicherstellen, dass page_content ein String ist
        if isinstance(page_content, Document):
            page_content = str(page_content)

        # Optional: Keywords aus einer anderen Quelle beziehen, falls nötig
        # keywords = keywords_per_chunk[i]  # Wenn du weiterhin auf die Keywords zugreifen möchtest

        # Beispiel-Keyword-String (falls du weiterhin einen benötigen solltest)
        # keywords_str = ", ".join(keywords)  # Dies kannst du anpassen, je nach Bedarf

        # Hinzufügen des Chunks mit den entsprechenden Metadaten und Embeddings
        collection.add(
            documents=[page_content],  # Der Seiteninhalt des Dokuments
            metadatas=[{"source": source}],  # Die Quelle als Metadaten
            ids=[doc_id],  # Eine eindeutige ID für jeden Eintrag
            embeddings=embeddings  # Die Embeddings als Liste von Listen
        )
        
        print(doc_id)

    print("Alle Chunks wurden erfolgreich mit ihren Embeddings und Metadaten zu Chroma hinzugefügt.")


# Beispielverwendung
def start_creating_chroma():
    """
    Initialisiert die Erstellung einer Chroma-Datenbank, indem verschiedene Dokumente verarbeitet, in Chunks unterteilt, mit Embeddings versehen und in die Datenbank eingefügt werden.

    Description:
        Diese Funktion führt mehrere Schritte aus, um eine Chroma-Datenbank zu erstellen:
        1. Zunächst wird die Chroma-Collection geleert, falls sie existiert.
        2. Markdown-Dateien aus einem Ordner werden geladen, in kleinere Chunks aufgeteilt und aufbereitet.
        3. Daten von der Overpass API (z.B. Recyclingstationen in Frankfurt) werden abgerufen, in Dokumente umgewandelt und ebenfalls in Chunks aufgeteilt.
        4. Die Chunks der Markdown-Dateien und der API-Daten werden kombiniert.
        5. Für alle kombinierten Chunks werden Embeddings erstellt.
        6. Die Dokumente zusammen mit ihren Embeddings und Metadaten werden in die Chroma-Datenbank eingefügt.

    Args:
        None

    Returns:
        None: Die Funktion gibt nichts zurück, führt aber mehrere Aktionen zur Erstellung der Chroma-Datenbank aus.
    """
    # Initialisieren Var
    collection_name='document_embeddings_v20'
    persist_directory='chroma_db_v4'
    md_folder_path = os.path.join('data', 'md_cleaned')
    chunk_size=500
    chunk_overlap=100
    # Overpass API URL (öffentlicher Overpass-Server)
    overpass_url = "https://overpass-api.de/api/interpreter"
    # Overpass Query für Mülltrennungsanlagen (Recyclingstationen) in Frankfurt am Main
    overpass_query = """
    [out:json];
    area["name"="Frankfurt am Main"]->.searchArea;
    (
    node["amenity"="recycling"](area.searchArea);
    way["amenity"="recycling"](area.searchArea);
    relation["amenity"="recycling"](area.searchArea);
    );
    out body;
    >;
    out skel qt;
    """
    
    # ChromaDB Cleanen
    delete_chroma_collection(collection_name, persist_directory)
    # MD Dateien Chunken und Vorbereiten
    md_docs_chunked = encode_md_from_folder(md_folder_path, chunk_size, chunk_overlap)
    # Overpass API to Documents
    api_docs = api_to_docs(overpass_url, overpass_query)
    api_docs_chunked = encode_api(api_docs, chunk_size, chunk_overlap)
    # Combine Lists
    # INFO: Hier könnte man auch noch den Webloader integieren
    docs_list = md_docs_chunked + api_docs_chunked
    
    docs_with_embeddings = add_embeddings(docs_list)
    
    create_chroma_v2(docs_with_embeddings, collection_name, persist_directory)

    # Gliederung der Dokumente
    # for document in docs_with_embeddings:
    #     print(f"Quelle: {document['metadata']['source']}")
    #     print("\nInhalt:")
    #     print(document['page_content'])
    #     print("\nEmbeddings:")
    #     print(document['embeddings'])
    #     print("\n" + "-"*50 + "\n")
    
    # for doc in docs_list:
    #     print(doc.page_content)

# ChromaDB Collection Löschen und neu erstellen
start_creating_chroma()


#########################################################################

# Test für Chroma auszulesen, zum testen einfach unten den Aufruf der Testfunktion auskommentieren

def get_similar_documents_from_chroma(collection_name, persist_directory, query, top_k=3):
    # Erstelle einen PersistentClient, um die Chroma-Datenbank zu öffnen
    client = chromadb.PersistentClient(
        path=persist_directory,
        settings=Settings(),
        tenant=DEFAULT_TENANT,
        database=DEFAULT_DATABASE,
    )
    
    # Lade die entsprechende Collection
    collection = client.get_collection(name=collection_name)
    
    # Erstelle die Embeddings für die Abfrage
    query_embeddings = create_query_embeddings(query).tolist()
    
    # Führe die Abfrage in der Collection durch und suche die ähnlichsten Dokumente
    results = collection.query(query_embeddings=query_embeddings, n_results=top_k)
    
    # Überprüfe den Aufbau des Ergebnisses und gib die Dokumente aus
    if 'documents' in results and 'metadatas' in results and 'distances' in results:
        for i, (document, metadata, distance) in enumerate(zip(results['documents'][0], results['metadatas'][0], results['distances'][0])):
            similarity_score = 1 / (1 + distance)  # Berechnung des Ähnlichkeitsscores
            print("Ähnlichkeitsscore:", similarity_score)
            print(f"Dokument {i+1}:")
            print("Inhalt:", document)
            print("Metadaten:", metadata)

            print()
    else:
        print("Keine ähnlichen Dokumente gefunden.")
        
    return results

def test():
    # Beispielaufruf der Funktion
    # query = "Was kommt in den Altglascontainer?"
    # query = "Was kommt in die gelbe Tonne?"
    query = "Welche Holzentsorgungen gibt es?"
    collection_name='document_embeddings_v20'
    persist_directory='chroma_db_v4'
    rag_results = get_similar_documents_from_chroma(collection_name, persist_directory, query)

# Zum Testen hier Auskommentieren
# test()
    
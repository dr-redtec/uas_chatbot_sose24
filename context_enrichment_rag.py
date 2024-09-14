import chromadb
from chromadb.config import DEFAULT_TENANT, DEFAULT_DATABASE, Settings
from embeddings import *
from llms import *


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
    # if 'documents' in results and 'metadatas' in results and 'distances' in results:
    #     for i, (document, metadata, distance) in enumerate(zip(results['documents'][0], results['metadatas'][0], results['distances'][0])):
    #         similarity_score = 1 / (1 + distance)  # Berechnung des Ähnlichkeitsscores
    #         print("Ähnlichkeitsscore:", similarity_score)
    #         print(f"Dokument {i+1}:")
    #         print("Inhalt:", document)
    #         print("Metadaten:", metadata)

    #         print()
    # else:
    #     print("Keine ähnlichen Dokumente gefunden.")
        
    return results

def get_chunk_by_index(doc_id, collection_name, persist_directory):
    # Erstelle einen PersistentClient, um die Chroma-Datenbank zu öffnen
    client = chromadb.PersistentClient(
        path=persist_directory,
        settings=Settings(),
        tenant=DEFAULT_TENANT,
        database=DEFAULT_DATABASE,
    )
    
    # Lade die entsprechende Collection
    collection = client.get_collection(name=collection_name)
    
    # Hole die Gesamtanzahl der Dokumente in der Collection
    total_docs = collection.count()

    # Speichere die Anzahl der Dokumente als int
    total_docs_as_int = int(total_docs)

    #print(f"Die Gesamtanzahl der Dokumente in der Collection ist: {total_docs_as_int}")
    
    # Extrahiere den numerischen Teil der doc_id
    base_id = doc_id.split('_')[-1]
    
    try:
        # Konvertiere in einen Integer
        base_id_num = int(base_id)
        
        # IDs vor und nach der aktuellen ID
        prev_id_num = base_id_num - 1
        next_id_num = base_id_num + 1
        
        # Verhindere, dass prev_id 0 oder kleiner wird
        if prev_id_num > 0:
            prev_id = f"id_{prev_id_num}"
        else:
            prev_id = None  # Keine gültige ID, wird später ignoriert

        # Verhindere, dass next_id die maximale ID überschreitet
        if next_id_num <= total_docs_as_int:
            next_id = f"id_{next_id_num}"
        else:
            next_id = None  # Keine gültige ID, wird später ignoriert

        # Dokument-IDs, die wir abfragen wollen
        document_ids = [prev_id, doc_id, next_id]

        # Leere Liste für die Ergebnisse
        documents_for_context = []

        # Schleife über die IDs und hole die Dokumente
        for id_batch in document_ids:
            if id_batch is not None:  # Nur wenn die ID gültig ist
                # Hole die Dokumente für die aktuelle ID
                results = collection.get(ids=[id_batch])
                
                # print(results)
                
                # Füge die Dokumente der Liste hinzu
                documents_for_context.append(results)  # assuming 'documents' contains the actual document data

        return documents_for_context
    except ValueError:
        print(f"Ungültiges ID-Format: {doc_id}")
        return None

def concatenate_documents(test):
    # Starte mit einem leeren String für den zusammengeführten Text
    concatenated_text = ""

    # Iteriere über jedes Dokument in der Liste
    for entry in test:
        current_document = entry['documents'][0]  # Da 'documents' eine Liste ist
        concatenated_text += current_document  # Füge den Inhalt hinzu
    
    return concatenated_text

def concatenate_documents_string(test):
    # Starte mit dem ersten Dokument in der Liste
    concatenated_text = test[0]['documents'][0]

    # Iteriere über die restlichen Dokumente
    for i in range(1, len(test)):
        current_document = test[i]['documents'][0]
        
        # Finde den längsten gemeinsamen Teil (Suffix des bisherigen Textes und Präfix des aktuellen)
        overlap_length = find_overlap(concatenated_text, current_document)
        
        # Füge den neuen Text ohne den überschneidenden Teil hinzu
        concatenated_text += current_document[overlap_length:]

    return concatenated_text

def find_overlap(text1, text2):
    """Finde den längsten gemeinsamen Teil zwischen dem Ende von text1 und dem Anfang von text2"""
    max_overlap = min(len(text1), len(text2))
    
    # Suche den längsten gemeinsamen Suffix-Präfix zwischen text1 und text2
    for i in range(max_overlap, 0, -1):
        if text1[-i:] == text2[:i]:
            return i
    return 0

def get_context_list(rag_results, collection_name, persist_directory):
    # Leere Liste für die Ergebnisse von get_chunk_by_index
    context_list = []

    if 'ids' in rag_results:
        for i, ids in enumerate(rag_results['ids'][0]):
            # print(f"Dokument {i+1}:")
            # print("Inhalt:", ids)
            get_context = get_chunk_by_index(ids, collection_name, persist_directory)
            concatenated_text_string = concatenate_documents_string(get_context)
            
            context_list.append(concatenated_text_string)
            # print(concatenated_text_string)
            # print()
            # filter_context += f"Dokument {i+1}:\n"
            # filter_context += f"Inhalt: {document}\n\n"
    else:
            print("Keine ähnlichen Dokumente gefunden.")


    return context_list

def create_context_for_llm(context_list):

    filter_context = ""
    # Überprüfe den Aufbau des Ergebnisses und gib die Dokumente aus
    # context_list

    for i, document in enumerate(context_list):
        # print(f"Dokument {i+1}:")
        # print("Inhalt:", document)
        # print()
        filter_context += f"Dokument {i+1}:\n"
        filter_context += f"Inhalt: {document}\n\n"

        
    return filter_context

def start_query_context(query):
    
    # Beispielaufruf der Funktion
    # query = "Was kommt in den Altglascontainer?"
    # query = "Was kommt in die gelbe Tonne?"
    # query = "Wie lautet die Telefonummer der FES?"
    collection_name='document_embeddings_v20'
    persist_directory='chroma_db_v4'
    rag_results = get_similar_documents_from_chroma(collection_name, persist_directory, query)
    context_list = get_context_list(rag_results, collection_name, persist_directory)
    # Initialisiere die Modelle
    mistral_model, llama_model = initialize_models()
    filter_context = create_context_for_llm(context_list)
    response_llm = ask_llm_with_ollama(query, filter_context, mistral_model)
    # print(context_list)
    # Schleife über die Elemente in der context_list und gib sie aus
    # for i, context in enumerate(context_list):
    #     print(f"Element {i+1}: {context}")
    # print(response_llm)
    return response_llm
    
    

# query = "Was kommt in den Altglascontainer?"
        
# start_query_context(query)
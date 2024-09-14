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

def create_context_for_llm(rag_results):

    filter_context = ""
    # Überprüfe den Aufbau des Ergebnisses und gib die Dokumente aus
    if 'documents' in rag_results:
        for i, document in enumerate(rag_results['documents'][0]):
            # print(f"Dokument {i+1}:")
            # print("Inhalt:", document)
            # print()
            filter_context += f"Dokument {i+1}:\n"
            filter_context += f"Inhalt: {document}\n\n"
    else:
        print("Keine ähnlichen Dokumente gefunden.")
        
    return filter_context

def start_query(query):
    
    mistral_model, llama_model = initialize_models()
    collection_name='document_embeddings_v20'
    persist_directory='chroma_db_v4'
    
    rag_results = get_similar_documents_from_chroma(collection_name, persist_directory, query)
    filter_context = create_context_for_llm(rag_results)
    
    response_llm_mistal = ask_llm_with_ollama(query, filter_context, mistral_model)

    return response_llm_mistal
    

# Beispielaufruf der Funktion
# query = "Wie entsorge ich mein Altglas?"
# query = "Wie lautet die Telefonummer der FES?"
# print(start_query(query))

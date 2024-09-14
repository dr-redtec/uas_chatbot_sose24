from embeddings import *
from llms import *
import re
from query_simple_rag import *

def start_query_transform(query):

    mistral_model, llama_model = initialize_models_query()
    response_llm = transform_query_with_ollama(query, mistral_model)
    # print(response_llm)
    return response_llm

def string_in_liste_aufteilen(text):
    # Wir verwenden eine reguläre Expression, um den String bei Zahlen und Fragezeichen aufzuteilen
    fragen = re.split(r'\d+\.\s', text)
    # Filtere mögliche leere Elemente heraus
    fragen = [frage.strip() for frage in fragen if frage]
    return fragen


def start_each_query(query):
    
    # print(liste)
    collection_name='document_embeddings_v20'
    persist_directory='chroma_db_v4'
    
    rag_results = get_similar_documents_from_chroma(collection_name, persist_directory, query)
    filter_context = create_context_for_llm(rag_results)
    return filter_context
    
    
def dokumente_ausgeben(liste):
    multi_filter_context = ""
    for i, dokument in enumerate(liste, 1):  # i ist der Index, dokument ist der Inhalt
        # print(f"{i}. {dokument}")
        multi_filter_context += f"Kontext {i+1}:\n"
        get_filter_context = start_each_query(dokument)
        multi_filter_context += f"{get_filter_context}\n\n"
        
    return multi_filter_context

def ask_llm_with_multi_context(query, multi_filtert_context_result):
    mistral_model, llama_model = initialize_models()
    response_llm_mistal = ask_llm_with_ollama(query, multi_filtert_context_result, mistral_model)

    return response_llm_mistal


def start_for_bot(query):
    query_transform_string = start_query_transform(query)
    liste = string_in_liste_aufteilen(query_transform_string)
    multi_filtert_context_result = dokumente_ausgeben(liste)
    answer = ask_llm_with_multi_context(query, multi_filtert_context_result)
    return answer

    
# query = "Was kommt in den Altglascontainer und was in die Altkleidersammlung? Fasse dich in 100 Wörter!"
# print(start_for_bot(query))
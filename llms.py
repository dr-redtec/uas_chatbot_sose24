from langchain_community.llms.ollama import Ollama

def initialize_models():
    """
    Initialisiert und gibt zwei Language Models (LLMs) zurück: Mistral und Llama, die über den Ollama-API-Server verfügbar sind.

    Description:
        Diese Funktion erstellt zwei Ollama-Instanzen, die mit den Modellen "mistral-nemo" und "llama3.1:8b" konfiguriert sind.
        Beide Modelle werden über denselben Ollama-API-Server angesprochen. Die Basis-URL des Servers wird in beiden Instanzen 
        auf "http://192.168.180.131:11434" gesetzt. Die Funktion gibt beide Modelle als Rückgabewerte zurück.

    Returns:
        tuple: Eine Tupel-Rückgabe, die die beiden initialisierten Modelle enthält (ollama_llm_mistral, ollama_llm_llama).
    """
    ollama_llm_mistral = Ollama(
        model="mistral-nemo",
        base_url="http://192.168.180.131:11434"
    )
    ollama_llm_llama = Ollama(
        model="llama3.1:8b",
        base_url="http://192.168.180.131:11434"
    )
    return ollama_llm_mistral, ollama_llm_llama

def initialize_models_query():
    """
    Initialisiert und gibt zwei Language Models (LLMs) zurück, die für Abfragen verwendet werden: Mistral und Llama, die über den Ollama-API-Server verfügbar sind.

    Description:
        Diese Funktion ist nahezu identisch mit `initialize_models()`, aber speziell für Abfragen konzipiert.
        Sie erstellt zwei Ollama-Instanzen, eine für das Modell "mistral-nemo" und eine für das Modell "llama3.1:8b". 
        Beide Modelle werden über denselben Ollama-API-Server angesprochen, der unter der Basis-URL "http://192.168.180.131:11434" erreichbar ist.
        Die Funktion gibt beide Modelle als Rückgabewerte zurück.

    Returns:
        tuple: Eine Tupel-Rückgabe, die die beiden initialisierten Modelle für Abfragen enthält (ollama_llm_mistral, ollama_llm_llama).
    """
    ollama_llm_mistral = Ollama(
        model="mistral-nemo",
        base_url="http://192.168.180.131:11434"
    )
    ollama_llm_llama = Ollama(
        model="llama3.1:8b",
        base_url="http://192.168.180.131:11434"
    )
    return ollama_llm_mistral, ollama_llm_llama

def ask_llm_with_ollama(query, filtered_context, llm):
    """
    Sendet eine Query an das LLM (Ollama), zusammen mit dem gefilterten Kontext.
    
    Parameters:
    - query: Die ursprüngliche Frage.
    - filtered_context: Der gefilterte Kontext, der für die Beantwortung verwendet werden soll.
    - llm: Das LLM-Objekt, das die Anfrage bearbeitet.
    
    Returns:
    - Die Antwort des LLM.
    """
    prompt_text = f"""
    Du bist ein hochqualifiziertes Sprachmodell, das darauf trainiert ist, basierend auf bereitgestellten Informationen präzise und relevante Antworten zu geben. Deine Antworten sollen sich ausschließlich auf die gestellte Frage beziehen, keine zusätzlichen Informationen enthalten und dürfen nicht länger als 2000 Zeichen sein. 

    Frage: '{query}'

    Kontext:
    Hier sind relevante Informationen, die dir bei der Beantwortung der Frage helfen können:

    {filtered_context}

    Bitte verwende den obigen Kontext, um die folgende Frage so genau wie möglich zu beantworten. Achte darauf, dass deine Antwort:
    - nur die wichtigsten und relevantesten Informationen aus dem Kontext nutzt,
    - keine Wiederholungen oder redundante Informationen enthält,
    - klar, kohärent und leicht verständlich ist,
    - keine unbestätigten Vermutungen oder zusätzliche Erklärungen gibt.

    Antwort:
    """
    
    response = llm.invoke(prompt_text)
    
    return response

def transform_query_with_ollama(query, llm):
    """
    Sendet eine Abfrage an das LLM (Ollama), um die ursprüngliche Anfrage in einfachere Unteranfragen zu zerlegen.

    Args:
        query (str): Die ursprüngliche Frage, die zerlegt werden soll.
        llm (Ollama): Das Language Model (LLM)-Objekt, das die Anfrage bearbeitet.

    Description:
        Diese Funktion erstellt einen Prompt für das LLM, in dem die ursprüngliche Abfrage in 1-4 einfachere Unteranfragen 
        aufgeteilt werden soll. Der Prompt gibt klare Anweisungen, wie das Modell die Anfrage zerlegen soll. 
        Beispiele werden im Prompt zur Verfügung gestellt, um das Modell zu unterstützen. Der resultierende Prompt wird an das 
        Modell gesendet, und die Antwort des Modells wird zurückgegeben. Die Antwort besteht nur aus der nummerierten Liste der Unteranfragen.

    Returns:
        str: Die Antwort des LLM, welche die nummerierte Liste der Unteranfragen enthält.
    """
    prompt_text = f"""
        Sie sind ein KI-Assistent, der komplexe Anfragen in einfachere Unteranfragen für ein RAG-System zerlegt. Angesichts der ursprünglichen Anfrage zerlegen Sie diese in 1-4 einfachere Unteranfragen. Diese Unteranfragen sollen eine umfassende Antwort auf die ursprüngliche Anfrage liefern.

	•	Falls es nur eine Frage ist, geben Sie diese als einzelne Unteranfrage in Listenform aus.
	•	Falls die Anfrage unnötige Informationen für das RAG-System enthält, entfernen Sie diese.
	•	Geben Sie die Unteranfragen immer nummeriert und in Listenform aus.

    Beispiele:

    Beispiel 1:
    Ursprüngliche Anfrage: Was kommt in die gelbe Tonne und was kommt in die blaue Tonne?

    Unteranfragen:

        1.	Was kommt in die gelbe Tonne?
        2.	Was kommt in die blaue Tonne?

    Beispiel 2:
    Ursprüngliche Anfrage: Wo entsorge ich mein Altglas? Fasse dich in 100 Wörter.

    Unteranfrage:

        1.	Wo entsorge ich mein Altglas?

    Hier ist die Anfrage, die du in Unteranfragen gliedern sollst:
    Ursprüngliche Anfrage: '{query}'
        
    Gebe nur die Liste an Unteranfragen aus!    
    """
    
    response = llm.invoke(prompt_text)
    
    return response

def ask_llm_with_ollama_on_hessisch(query, llm):
    """
    Sendet eine Query an das LLM (Ollama), zusammen mit dem gefilterten Kontext.
    
    Parameters:
    - query: Die ursprüngliche Frage.
    - filtered_context: Der gefilterte Kontext, der für die Beantwortung verwendet werden soll.
    - llm: Das LLM-Objekt, das die Anfrage bearbeitet.
    
    Returns:
    - Die Antwort des LLM.
    """
    prompt_text = f"""
    Du bist ein Sprachmodell, das darauf spezialisiert ist, Texte in den hessischen Dialekt zu übersetzen. Bitte übersetze den folgenden Text so authentisch wie möglich in den hessischen Dialekt:

    Text: '{query}'

    Übersetzung in hessischen Dialekt:
    """
    
    response = llm.invoke(prompt_text)
    
    return response
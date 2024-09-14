from langchain.vectorstores.chroma import Chroma
from langchain.prompts import ChatPromptTemplate
from langchain_community.llms.ollama import Ollama
from langchain_community.embeddings.ollama import OllamaEmbeddings

CHROMA_PATH = "chroma"

PROMPT_TEMPLATE = """
Answer the question based only on the following context:

{context}

---

Answer the question based on the above context: {question}
"""

def get_embedding_function():
    # Verwende OllamaEmbeddings mit deinem lokalen Ollama-Server und dem Modell "llama3.1:8b"
    embeddings = OllamaEmbeddings(
        model="llama3.1:8b",  # Modellname, wie auf dem Server konfiguriert
        base_url="http://192.168.180.131:11434"  # IP-Adresse und Port deines Servers
    )
    return embeddings

def query_rag(query_text: str):
    # Prepare the DB.
    embedding_function = get_embedding_function()
    db = Chroma(persist_directory=CHROMA_PATH, embedding_function=embedding_function)

    # Search the DB.
    results = db.similarity_search_with_score(query_text, k=5)

    # Print out the chunks retrieved from the Chroma database
    #print("Retrieved Chunks:")
    #for i, (doc, score) in enumerate(results):
    #    print(f"Chunk {i+1}:")
    #    print(f"Score: {score}")
    #    print(f"Content: {doc.page_content}")
    #    print(f"Metadata: {doc.metadata}")
    #    print("\n---\n")

    context_text = "\n\n---\n\n".join([doc.page_content for doc, _score in results])
    prompt_template = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
    prompt = prompt_template.format(context=context_text, question=query_text)

    # Use local Ollama model with llama3.1 8b
    model = Ollama(
        model="llama3.1:8b", 
        base_url="http://192.168.180.131:11434"  # IP-Adresse und Port deines Servers
    )
    response_text = model.invoke(prompt)

    # Collect sources
    sources = []
    for doc, _score in results:
        source_id = doc.metadata.get("id", "Unknown Source")  # Verwenden Sie 'Unknown Source', wenn 'id' fehlt
        sources.append(source_id)

    #formatted_response = f"Response: {response_text}\nSources: {sources}"
    formatted_response = f"{response_text}"
    print(formatted_response)
    return response_text

# Direkt im Notebook ausführen
query_text = "In welche Tonne kommt Bio Müll?"  # Setzen Sie hier Ihren Abfragetext ein
query_rag(query_text)
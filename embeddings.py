from sentence_transformers import SentenceTransformer


# Text-zu-Vektor Modell laden (z.B. SentenceTransformer)
# model = SentenceTransformer('sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')  
# paraphrase-German-distilbert-base-v2 --> Privat
# sentence-transformers/paraphrase-German-distilbert-base-v2
# model = SentenceTransformer("sentence-transformers/distiluse-base-multilingual-cased-v2")
# model = SentenceTransformer('Alibaba-NLP/gte-Qwen1.5-7B-instruct')

# model = SentenceTransformer("sentence-transformers/distiluse-base-multilingual-cased-v2")
model = SentenceTransformer("intfloat/multilingual-e5-large")

def create_embeddings(chunk):
    
    prefix = "passage: "
    new_chunk = prefix + chunk
    # Erstelle Embeddings für die Texte
    chunk_embedding = model.encode(new_chunk, normalize_embeddings=True)
    print("Embedding erstellt")
    return chunk_embedding

def create_query_embeddings(chunk):
    
    prefix = "query: "
    new_chunk = prefix + chunk
    # Erstelle Embeddings für die Texte
    chunk_embedding = model.encode(new_chunk, normalize_embeddings=True)

    print("Embedding erstellt")
    return chunk_embedding

# def create_embeddings(chunk):
        
#     # Erstelle Embeddings für die Texte
#     chunk_embedding = model.encode(chunk, normalize_embeddings=True)

#     print("Embedding erstellt")
#     return chunk_embedding

# # test
# test = "Das ist ein Test."
# print(create_embeddings(test))
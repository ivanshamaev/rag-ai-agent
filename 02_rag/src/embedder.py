import chromadb
from chromadb.utils import embedding_functions

def create_chroma_db(chunks, persist_dir="embeddings"):
    client = chromadb.PersistentClient(path=persist_dir)
    sentence_ef = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name="all-MiniLM-L6-v2"
    )
    collection = client.get_or_create_collection(
        name="tables", embedding_function=sentence_ef
    )
    for i, chunk in enumerate(chunks):
        collection.add(documents=[chunk], ids=[str(i)])
    return collection
import json
from sentence_transformers import SentenceTransformer
import chromadb

model = SentenceTransformer("BAAI/bge-small-en-v1.5")
client = chromadb.PersistentClient(path="chroma_db")
collection = client.get_collection("fastapi_docs")

prefix = "Represent this sentence for searching relevant passages: "

def retrieve(question, k=5):
    query_vec = model.encode(prefix + question, normalize_embeddings=True)
    result = collection.query(query_embeddings=[query_vec], n_results=k)
    chunks = []
    for doc, meta, dist in zip(result["documents"][0],
                               result["metadatas"][0],
                               result["distances"][0]):
        chunks.append({
            "text": doc,
            "url": meta["url"],
            "heading": meta["heading"],
            "distance": dist,
        })
    return chunks

import json
from sentence_transformers import SentenceTransformer
import chromadb

model = SentenceTransformer("BAAI/bge-small-en-v1.5")

chunks = []
token_lens = []
with open("chunks.jsonl", encoding="utf-8") as f:
    for line in f:
        chunk = json.loads(line)
        chunks.append(chunk)
        token_lens.append(len(model.tokenizer.tokenize(chunk["text"])))

texts = []
ids = []
metadatas = []
for ch in chunks:
    texts.append(ch["text"])
    ids.append(ch["id"])
    metadata = {
        "url": ch["url"],
        "title": ch["title"],
        "chunk_part":ch["chunk_part"],
        "heading":ch["heading"]
    }
    metadatas.append(metadata)
print(len(texts))

embeddings = model.encode(texts, batch_size=32, show_progress_bar=True,normalize_embeddings=True)
print(embeddings.shape)

client = chromadb.PersistentClient(path="chroma_db")
collection = client.get_or_create_collection("fastapi_docs", metadata={"hnsw:space": "cosine"})

collection.upsert(ids = ids, embeddings = embeddings, metadatas = metadatas, documents = texts)
print(collection.count())

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

for ch in retrieve("how does dependency injection work", k=6):
    print(round(ch["distance"], 3), ch["heading"], ch["url"])
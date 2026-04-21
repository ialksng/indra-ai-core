from sentence_transformers import SentenceTransformer
import numpy as np
from modules.memory.db import memory_collection

embed_model = SentenceTransformer("all-MiniLM-L6-v2")

def add_memory(user_id, texts):
    embeddings = embed_model.encode(texts).tolist()

    docs = [
        {
            "user_id": user_id,
            "text": text,
            "embedding": emb
        }
        for text, emb in zip(texts, embeddings)
    ]

    memory_collection.insert_many(docs)

def search_memory(user_id, query, k=3):
    q_emb = embed_model.encode([query])[0]

    docs = list(memory_collection.find({"user_id": user_id}))

    if not docs:
        return []

    def score(doc):
        emb = np.array(doc["embedding"])
        return np.dot(q_emb, emb)

    ranked = sorted(docs, key=score, reverse=True)

    return [d["text"] for d in ranked[:k]]
import numpy as np
from sentence_transformers import SentenceTransformer
import chromadb
import uuid
from typing import List, Dict, Any, Tuple
from sklearn.metrics.pairwise import cosine_similarity

_model = None

def get_model():
    global _model
    if _model is None:
        print("[MODEL] SentenceTransformer load ho raha hai...")
        _model = SentenceTransformer('all-MiniLM-L6-v2')
        print("[MODEL] Load complete!")
    return _model
class EmbedderManager:
    def __init__(self, model_name: str = 'all-MiniLM-L6-v2', collection_name: str = "documents"):
        self.model = get_model()
        self.client = chromadb.PersistentClient(path="./chroma_db")
        self.collection = self.client.get_or_create_collection(name=collection_name) 

    def embed_text(self, text: str) -> np.ndarray:
        return self.model.encode(text)

    def add_document(self, doc_id: str, text: str, title: str = "", source: str = ""):
        embedding = self.embed_text(text)
        self.collection.add(
            ids=[doc_id],
              embeddings=[embedding.tolist()],
                metadatas=[{
                    "text": text,
                    "title": title,  
                    "source": source
                    }])

    def search_similar(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        query_embedding = self.embed_text(query).reshape(1, -1)
        results = self.collection.query(query_embeddings=query_embedding.tolist(), n_results=top_k)
        return results['metadatas'][0]
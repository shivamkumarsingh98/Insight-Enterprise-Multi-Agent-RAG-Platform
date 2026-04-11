from app.embeddings.embed import EmbedderManager

class ChromaDBManager:
    def __init__(self):
        self.embedder = EmbedderManager()
        

    def add_document(self, doc_id: str, text: str, title: str = "", source: str = ""):
        self.embedder.add_document(doc_id, text, title, source)

    def search_similar(self, query: str, top_k: int = 5):
        return self.embedder.search_similar(query, top_k)
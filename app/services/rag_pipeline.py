# from app.data_ingestion.ingest import ingest_data
# from app.chunking.chunk import chunk_documents
# from app.vector_db.croma_db import ChromaDBManager
# from langchain_core.documents import Document
# import uuid

# db = ChromaDBManager()  # ek baar initialize karo

# def run_rag_pipeline(query: str):

#     # ✅ Step 1: query
#     print(f"\n[1] QUERY: {query}")

#     # ✅ Step 2: ingest — arXiv se papers aate hain
#     data = ingest_data(query)
#     print(f"[2] INGEST: {len(data)} papers mile")
#     for i, item in enumerate(data):
#         print(f"    [{i+1}] {item.get('title', 'No title')}")

#     # ✅ Step 3: Document objects banao
#     documents = [
#         Document(
#             page_content=item.get("summary", ""),
#             metadata={
#                 "title": item.get("title", ""),
#                 "source": item.get("link", "")
#             }
#         )
#         for item in data
#     ]
#     print(f"[3] DOCUMENTS: {len(documents)} documents bane")

#     # ✅ Step 4: chunk karo
#     chunks = chunk_documents(documents)
#     print(f"[4] CHUNKS: {len(chunks)} chunks bane")
#     print(f"    Pehla chunk preview: {chunks[0].page_content[:100]}..." if chunks else "    Koi chunk nahi!")

#     # ✅ Step 5: embed + store ChromaDB mein
#     print(f"[5] EMBED + STORE: ChromaDB mein daal rahe hain...")
#     for chunk in chunks:
#         doc_id = str(uuid.uuid4())
#         db.add_document(doc_id=doc_id, text=chunk.page_content)
#     print(f"    {len(chunks)} chunks store ho gaye")

#     # ✅ Step 6: search — query se similar chunks dhundho
#     print(f"[6] SEARCH: query se similar chunks dhundh rahe hain...")
#     similar_chunks = db.search_similar(query, top_k=5)
#     print(f"    {len(similar_chunks)} similar chunks mile")
#     for i, chunk in enumerate(similar_chunks):
#         print(f"    [{i+1}] {chunk.get('text', '')[:80]}...")

#     # ✅ Step 7: answer — relevant text return karo
#     print(f"[7] ANSWER: context ready\n")
#     context = "\n\n".join([c.get("text", "") for c in similar_chunks])
#     return [ {
#         "title": c.get("title", ""),
#             "summary": c.get("text", ""),
#             "link": c.get("source", "")
#     }
#     for c in similar_chunks
#     ]

from app.data_ingestion.ingest import ingest_data
from app.chunking.chunk import chunk_documents
from app.embeddings.embed import EmbedderManager
from langchain_core.documents import Document
import uuid

def run_rag_pipeline(query: str):

    # Step 1
    print(f"\n[1] QUERY: {query}")

    # Step 2: ingest
    data = ingest_data(query)
    print(f"[2] INGEST: {len(data)} papers mile")
    for i, item in enumerate(data):
        print(f"    [{i+1}] {item.get('title', 'No title')}")

    # Step 3: Documents
    documents = [
        Document(
            page_content=item.get("summary", ""),
            metadata={
                "title": item.get("title", ""),
                "source": item.get("link", "")
            }
        )
        for item in data
    ]
    print(f"[3] DOCUMENTS: {len(documents)} documents bane")

    # Step 4: chunk
    chunks = chunk_documents(documents)
    print(f"[4] CHUNKS: {len(chunks)} chunks bane")

    # ✅ Step 5: har query ke liye FRESH collection banao
    print(f"[5] EMBED + STORE: Fresh collection bana rahe hain...")
    embedder = EmbedderManager(collection_name=f"query_{uuid.uuid4().hex[:8]}")
    for chunk in chunks:
        doc_id = str(uuid.uuid4())
        embedder.add_document(doc_id=doc_id, text=chunk.page_content, title=chunk.metadata.get("title", ""),   # ✅
        source=chunk.metadata.get("source", "") )
    print(f"    {len(chunks)} chunks store ho gaye")

    # Step 6: search
    print(f"[6] SEARCH: similar chunks dhundh rahe hain...")
    similar_chunks = embedder.search_similar(query, top_k=5)
    print(f"    {len(similar_chunks)} similar chunks mile")
    for i, c in enumerate(similar_chunks):
        print(f"    [{i+1}] {c.get('text', '')[:80]}...")

    # Step 7
    print(f"[7] ANSWER: context ready\n")
    return [
        {
            "title": c.get("title", ""),
            "summary": c.get("text", ""),
            "link": c.get("source", "")
        }
        for c in similar_chunks
    ]
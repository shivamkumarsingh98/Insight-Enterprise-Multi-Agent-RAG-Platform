# from app.data_ingestion.ingest import ingest_data
# from langchain_core.documents import Document
# from langchain_text_splitters import RecursiveCharacterTextSplitter

# def chunk_documents(documents: list[Document], chunk_size: int = 1000, chunk_overlap: int = 200) -> list[Document]:
#     text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
#     chunks = []
#     for doc in documents:
#         doc_chunks = text_splitter.split_text(doc.page_content)
#         for i, chunk in enumerate(doc_chunks):
#             chunk_doc = Document(
#                 page_content=chunk,
#                 metadata={
#                     "source": f"{doc.metadata.get('source', 'unknown')}_chunk_{i}",
#                     **doc.metadata
#                 }
#             )
#             chunks.append(chunk_doc)
#     return chunks


from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter


def chunk_documents(documents: list[Document], chunk_size: int = 1000, chunk_overlap: int = 200) -> list[Document]:

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap
    )

    return text_splitter.split_documents(documents)

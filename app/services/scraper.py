from langchain_community.document_loaders import WebBaseLoader

class ScraperService:
    def scrape(self, url: str):
        loader = WebBaseLoader(url)
        docs = loader.load()
        return docs
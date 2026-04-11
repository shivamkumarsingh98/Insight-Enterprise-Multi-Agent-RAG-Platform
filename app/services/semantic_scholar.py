# # app/services/semantic_scholar.py

# import requests
# import time

# def search_papers(query: str, max_results: int = 5) -> list:
#     url = "https://api.openalex.org/works"

#     params = {
#         "search": query,
#         "per-page": max_results,
#         "select": "title,abstract_inverted_index,authorships,publication_year,doi,primary_location",
#         "mailto": "your@email.com"  # ✅ polite pool — faster responses
#     }

#     try:
#         response = requests.get(url, params=params, timeout=10)
#         response.raise_for_status()
#         data = response.json()

#         results = []
#         for work in data.get("results", []):

#             # OpenAlex abstract inverted index se text banao
#             abstract = reconstruct_abstract(work.get("abstract_inverted_index"))

#             # Link banao
#             doi = work.get("doi")
#             link = doi if doi else work.get("primary_location", {}).get("landing_page_url", "")

#             results.append({
#                 "title": work.get("title", "No title"),
#                 "authors": [
#                     a["author"]["display_name"]
#                     for a in work.get("authorships", [])[:3]  # sirf 3 authors
#                 ],
#                 "summary": abstract[:300],
#                 "published": str(work.get("publication_year", "Unknown")),
#                 "link": link or ""
#             })

#         print(f"    OpenAlex se {len(results)} papers mile")
#         return results

#     except requests.exceptions.RequestException as e:
#         print(f"[ERROR] OpenAlex API error: {e}")
#         return []


# def reconstruct_abstract(inverted_index: dict) -> str:
#     """OpenAlex abstract inverted index ko normal text mein convert karo"""
#     if not inverted_index:
#         return "No abstract available"

#     # {word: [positions]} → position se sort karke join karo
#     words = []
#     for word, positions in inverted_index.items():
#         for pos in positions:
#             words.append((pos, word))

#     words.sort(key=lambda x: x[0])
#     return " ".join(w for _, w in words)

# app/services/semantic_scholar.py

from ddgs import DDGS
import time

def search_papers(query: str, max_results: int = 5) -> list:
    results = []

    try:
        with DDGS() as ddgs:
            search_results = list(ddgs.text(
                query,
                max_results=max_results
            ))

        for item in search_results:
            results.append({
                "title": item.get("title", "No title"),
                "authors": [],
                "summary": item.get("body", "No summary available")[:300],
                "published": "Web",
                "link": item.get("href", "")
            })

        print(f"    DuckDuckGo se {len(results)} results mile")
        return results

    except Exception as e:
        print(f"[ERROR] DuckDuckGo search error: {e}")
        return []
# app/agents/search_agent.py

# import arxiv

# def search_papers(query, max_results=5):
    
#     search = arxiv.Search(
#         query=query,
#         max_results=max_results,
#         sort_by=arxiv.SortCriterion.RELEVANT,
#     )
#     results = []
#     for result in search.results():
#         results.append({
#             "title": result.title,
#             "authors": [author.name for author in result.authors],
#             "summary": result.summary,
#             "published": result.published,
#             "link": result.entry_id,
#         })
#     return results

# app/agents/search_agent.py
# app/agents/search_agent.py

# from app.services.arxiv import search_arxiv

# def search_agent(query: str, max_results: int = 5):
#     return search_arxiv(query, max_results)

from app.services.semantic_scholar import search_papers  

def search_agent(query: str, max_results: int = 5):
    return search_papers(query, max_results)
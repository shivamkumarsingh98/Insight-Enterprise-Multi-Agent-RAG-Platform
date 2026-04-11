from arxiv import Search, SortCriterion, SortOrder

def search_arxiv(query, max_results=5):
    search = Search(
        query=query,
        max_results=max_results,
        sort_by=SortCriterion.SubmittedDate,
        sort_order=SortOrder.Descending,
    )

    results = []
    for result in search.results():
        results.append({
            "title": result.title,
            "authors": [author.name for author in result.authors],
            "summary": result.summary,
            "published": result.published,
            "link": result.entry_id,
        })

    return results
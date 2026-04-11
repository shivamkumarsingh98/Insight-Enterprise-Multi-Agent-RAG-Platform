from app.agents.workflow import run_workflow

def ingest_data(query: str):
    if not query.strip():
        raise ValueError("Query parameter cannot be empty")
    results = run_workflow(query)
    print(results)
    return results
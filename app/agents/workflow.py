# app/agents/workflow_agent.py

# app/agents/workflow_agent.py
# app/agents/workflow_agent.py

from langgraph.graph import StateGraph

from app.agents.search_agent import search_agent
from app.agents.summarize_agent import summarize_agent

# -------------------------
# Nodes (agents as functions)
# -------------------------

def search_node(state):
    query = state["query"]
    papers = search_agent(query)
    return {"papers": papers}


def summarize_node(state):
    papers = state["papers"]

    results = []
    for paper in papers:
        summary = summarize_agent(paper)
        results.append({
            "title": paper["title"],
            "summary": summary,
            "link": paper["link"]
        })

    return {"results": results}


# -------------------------
# Graph builder
# -------------------------

def build_graph():
    builder = StateGraph(dict)

    builder.add_node("search", search_node)
    builder.add_node("summarize", summarize_node)

    builder.set_entry_point("search")
    builder.add_edge("search", "summarize")

    return builder.compile()


# -------------------------
# Run workflow
# -------------------------

graph = build_graph()

def run_workflow(query: str):
    result = graph.invoke({"query": query})
    return result["results"]

# from app.agents.search_agent import SearchAgent
# from app.agents.summarize_agent import SummarizeAgent

# class WorkflowAgent(Agent):
#     def run(self, query):
#         search_agent = SearchAgent()
#         summarize_agent = SummarizeAgent()
        
#         # पहला स्टेप: सर्च
#         papers = search_agent.run(query)
        
#         # दूसरा स्टेप: समरी
#         summarized_papers = []
#         for paper in papers:
#             summary = summarize_agent.run(paper)
#             summarized_papers.append({
#                 "title": paper['title'],
#                 "summary": summary,
#                 "link": paper['link'],
#             })
        
#         return summarized_papers

# from app.agents.search_agent import search_papers
# from app.agents.summarize_agent import summarize_paper

# def run_workflow(query, max_results=5):
#     # सबसे पहले, सर्च करो
#     papers = search_papers(query, max_results)
#     # अब हर पेपर का सारांश तैयार करो
#     results = []
#     for paper in papers:
#         summary = summarize_paper(paper)
#         results.append({
#             "title": paper['title'],
#             "authors": paper['authors'],
#             "published": paper['published'],
#             "summary": summary,
#             "link": paper['link'],
#         })
#     return results
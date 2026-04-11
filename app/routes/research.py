# app/routes/research.py

# from fastapi import APIRouter, HTTPException
# from fastapi.responses import StreamingResponse
# from app.supervisor.supervisor import supervisor
# from app.memory.short_term import memory
# from app.memory.long_term import long_term_memory
# from app.core.logging import get_logger
# # from app.agents.workflow import run_workflow
# from app.services.rag_pipeline import run_rag_pipeline
# from app.utils.pdf import generate_pdf
# import json
# from app.registry.agent_registry import registry

# logger = get_logger("routes")
# router = APIRouter()

# @router.get("/search")
# def search(query: str):
#     if not query.strip():
#         raise HTTPException(status_code=400, detail="Query parameter cannot be empty")
#     # results = run_workflow(query)
#     results = run_rag_pipeline(query)
#     return {
#         "query": query,
#         "results": results
#     }

# @router.post("/generate-pdf")
# def generate_pdf_endpoint(results: list):
#     try:
#         pdf_buffer = generate_pdf(results)
#         return StreamingResponse(
#             pdf_buffer,
#             media_type="application/pdf",
#             headers={"Content-Disposition": "attachment; filename=research_results.pdf"}
#         )
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))
    
# @router.get("/agents")
# def get_agents():
#     """Kaun kaun se agents available hain — live status"""
#     return {
#         "agents": registry.get_all(),
#         "healthy_count": len(registry.get_healthy_agents())
#     }

# @router.get("/session/{session_id}")
# def get_session(session_id: str):
#     session = memory.get_session(session_id)
#     if not session:
#         raise HTTPException(status_code=404, detail="Session not found or expired")
#     return session.to_dict()

# @router.get("/session/{session_id}/history")
# def get_history(session_id: str):
#     session = memory.get_session(session_id)
#     if not session:
#         raise HTTPException(status_code=404, detail="Session not found")
#     return {"history": session.get_history()}

# @router.get("/user/{user_id}/history")
# def get_user_history(user_id: str):
#     return {
#         "user_id": user_id,
#         "query_history": long_term_memory.get_query_history(user_id)
#     }



# @router.get("/memory/stats")
# def memory_stats():
#     return memory.get_stats()


# app/routes/research.py

from fastapi import APIRouter, HTTPException, Query, Depends, Request
import time
from fastapi.responses import StreamingResponse
from app.supervisor.supervisor import supervisor
from app.memory.short_term import memory
from app.memory.long_term import long_term_memory
from app.core.logging import get_logger, get_correlation_id
from app.core.security import require_role, get_api_key, API_KEY_ROLES
from app.registry.agent_registry import registry
from app.governance.audit import audit_trail
from app.evaluation.evaluator import evaluator
from app.agents.classifier_agent import classifier
from app.mcp.mcp_server import mcp_server
from app.services.rag_pipeline import run_rag_pipeline
from app.utils.pdf import generate_pdf
import json
from app.agents.deep_research_agent import deep_research_agent
from app.agents.arxiv_agent import arxiv_agent
from app.agents.citation_agent import citation_agent
from app.agents.rerank_agent import rerank_agent
from fastapi.responses import StreamingResponse
import asyncio

logger = get_logger("routes")
router = APIRouter()


@router.get("/search")
def search(
    query: str,
    request: Request,
    session_id: str = None,
    user_id: str = "anonymous",
    auth=Depends(require_role("user"))
):
    if not query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")

    cid = get_correlation_id()
    start = time.time()

    # 1. Classify intent — Semantic Router Pattern
    classification = classifier.classify(query)
    intent = classification.intent.value
    confidence = classification.confidence

    # 2. LLM Fallback — confidence < 0.4 pe deep research use karo
    if confidence < 0.4:
        intent = "research_search"   # safe default
        logger.info("Low confidence — defaulting to research_search",
            confidence=confidence)

    logger.info("Intent classified",
        intent=intent, confidence=confidence)

    # 3. Supervisor ko intent ke saath call karo
    outcome = supervisor.run(query, session_id=session_id,
                             user_id=user_id, intent=intent)
    duration_ms = round((time.time() - start) * 1000, 2)

    results = outcome.get("results", [])

    audit_trail.log_api_call(
        user_id=user_id,
        session_id=outcome.get("session_id", ""),
        endpoint="/search",
        query=query,
        result_count=len(results),
        duration_ms=duration_ms,
        correlation_id=cid
    )

    eval_result = evaluator.evaluate(query, results, duration_ms)

    response = {
        "query": query,
        "session_id": outcome.get("session_id"),
        "intent": classification.to_dict(),
        "results": results,
        "meta": {
            **outcome.get("meta", {}),
            "correlation_id": cid,
            "role": auth["role"]
        }
    }
    if eval_result:
        response["evaluation"] = eval_result.to_dict()

    return response


@router.post("/generate-pdf")
def generate_pdf_endpoint(
    results: list,
    auth=Depends(require_role("user"))
):
    try:
        pdf_buffer = generate_pdf(results)
        return StreamingResponse(
            pdf_buffer,
            media_type="application/pdf",
            headers={"Content-Disposition": "attachment; filename=research_results.pdf"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/agents")
def get_agents(auth=Depends(require_role("user"))):
    return {
        "agents": registry.get_all(),
        "healthy_count": len(registry.get_healthy_agents())
    }


@router.get("/tools")
def get_tools(auth=Depends(require_role("user"))):
    """MCP tools — kaunse tools available hain"""
    return {"tools": mcp_server.list_tools()}


@router.get("/session/{session_id}")
def get_session(session_id: str, auth=Depends(require_role("user"))):
    session = memory.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found or expired")
    return session.to_dict()


@router.get("/session/{session_id}/history")
def get_history(session_id: str, auth=Depends(require_role("user"))):
    session = memory.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return {"history": session.get_history()}


@router.get("/user/{user_id}/history")
def get_user_history(user_id: str, auth=Depends(require_role("user"))):
    return {
        "user_id": user_id,
        "query_history": long_term_memory.get_query_history(user_id)
    }


@router.get("/memory/stats")
def memory_stats(auth=Depends(require_role("admin"))):
    return memory.get_stats()


@router.get("/audit/recent")
def get_audit_log(
    limit: int = 50,
    auth=Depends(require_role("admin"))
):
    """Sirf admin dekh sakta hai"""
    return {"events": audit_trail.get_recent(limit)}


@router.get("/evaluation/stats")
def eval_stats(auth=Depends(require_role("admin"))):
    return evaluator.get_stats()


@router.get("/health/detailed")
def detailed_health(auth=Depends(require_role("admin"))):
    return {
        "agents": registry.get_all(),
        "memory": memory.get_stats(),
        "tools": mcp_server.list_tools(),
        "evaluation": evaluator.get_stats()
    }

@router.get("/deep-research")
def deep_research(
    query: str,
    session_id: str = Query(default=None),
    user_id: str = Query(default=None),
    auth: dict = Depends(require_role("any"))
):
    """PhD/UPSC level deep research — multi-source comprehensive report"""
    if not query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")

    start = time.time()
    result = deep_research_agent(query)

    # Citations bhi generate karo
    citations = citation_agent(result["sources"])
    result["citations"] = citations

    # Audit log
    from app.governance.audit import audit_trail, AuditEvent
    from app.core.logging import get_correlation_id
    audit_trail.log_api_call(
        user_id=auth.get("key", "anonymous"),
        session_id=session_id or "",
        endpoint="/deep-research",
        query=query,
        result_count=result["total_sources"],
        duration_ms=round((time.time() - start) * 1000, 2),
        correlation_id=get_correlation_id()
    )

    return result


@router.get("/arxiv-search")
def arxiv_search(
    query: str,
    max_results: int = Query(default=5, le=20),
    auth: dict = Depends(require_role("any"))
):
    """Sirf arxiv.org se academic papers"""
    if not query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")

    results = arxiv_agent(query, max_results=max_results)
    ranked = rerank_agent(results, query)
    citations = citation_agent(ranked)

    return {
        "query": query,
        "results": ranked,
        "citations": citations,
        "total": len(ranked)
    }


@router.get("/deep-research/stream")
async def deep_research_stream(
    query: str,
    auth: dict = Depends(require_role("any"))
):
    """
    Streaming deep research — frontend ko real-time updates milenge.
    UI freeze nahi hoga.
    """
    if not query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")

    async def event_generator():
        try:
            # Step 1: Started
            yield f"data: {json.dumps({'step': 'started', 'message': 'Research started...', 'query': query})}\n\n"
            await asyncio.sleep(0.1)

            # Step 2: Classifying
            classification = classifier.classify(query)
            yield f"data: {json.dumps({'step': 'classified', 'intent': classification.intent.value, 'confidence': classification.confidence})}\n\n"
            await asyncio.sleep(0.1)

            # Step 3: Sub-queries generate karo
            from app.agents.deep_research_agent import _generate_subqueries
            subqueries = _generate_subqueries(query)
            yield f"data: {json.dumps({'step': 'subqueries', 'subqueries': subqueries, 'message': f'{len(subqueries)} sub-queries generated'})}\n\n"
            await asyncio.sleep(0.1)

            # Step 4: Per sub-query search karo
            from app.agents.arxiv_agent import arxiv_agent as arxiv_search
            from app.agents.search_agent import search_agent as web_search
            all_results = []
            seen_titles = set()

            for i, subq in enumerate(subqueries):
                yield f"data: {json.dumps({'step': 'searching', 'message': f'Searching: {subq}', 'progress': i+1, 'total': len(subqueries)})}\n\n"

                arxiv_results = arxiv_search(subq, max_results=3)
                for r in arxiv_results:
                    if r["title"] not in seen_titles:
                        seen_titles.add(r["title"])
                        all_results.append(r)

                web_results = web_search(subq, max_results=2)
                for r in web_results:
                    if r["title"] not in seen_titles:
                        seen_titles.add(r["title"])
                        all_results.append(r)

                await asyncio.sleep(0.5)

            yield f"data: {json.dumps({'step': 'collected', 'message': f'{len(all_results)} sources found', 'source_count': len(all_results)})}\n\n"
            await asyncio.sleep(0.1)

            # Step 5: Report synthesize karo
            yield f"data: {json.dumps({'step': 'synthesizing', 'message': 'Generating comprehensive report...'})}\n\n"

            from app.agents.deep_research_agent import _synthesize_report
            from app.agents.citation_agent import citation_agent as cite
            from app.agents.rerank_agent import rerank_agent as rerank

            ranked = rerank(all_results, query, top_k=8)
            report = _synthesize_report(query, ranked)
            citations = cite(ranked)

            # Step 6: Final result
            final = {
                "step": "completed",
                "query": query,
                "report": report,
                "sources": ranked,
                "citations": citations,
                "total_sources": len(ranked),
                "subqueries": subqueries
            }
            yield f"data: {json.dumps(final)}\n\n"

        except Exception as e:
            yield f"data: {json.dumps({'step': 'error', 'message': str(e)})}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",   # Nginx ke liye
            "Access-Control-Allow-Origin": "*"
        }
    )


@router.get("/health/detailed")
def detailed_health(auth=Depends(require_role("admin"))):
    from app.core.circuit_breaker import circuit_registry
    return {
        "agents": registry.get_all(),
        "memory": memory.get_stats(),
        "tools": mcp_server.list_tools(),
        "evaluation": evaluator.get_stats(),
        "circuit_breakers": circuit_registry.get_all_status()  # ← new
    }
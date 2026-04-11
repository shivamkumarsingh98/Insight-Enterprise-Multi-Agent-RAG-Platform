# from fastapi import FastAPI
# from fastapi.middleware.cors import CORSMiddleware
# from app.routes import research

# app = FastAPI()

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],  # Allow all origins for development
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# app.include_router(research.router)

# app/main.py

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from app.routes import research
from app.core.config import settings
from app.core.logging import setup_logging, set_correlation_id, generate_correlation_id, get_logger
import time
from app.registry.register_agents import register_all_agents

# Logging setup — sabse pehle
setup_logging("DEBUG" if settings.DEBUG else "INFO")
logger = get_logger("main")

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    debug=settings.DEBUG
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def correlation_middleware(request: Request, call_next):
    """Har request ko unique ID milega — trace karna easy hoga"""
    cid = request.headers.get("X-Correlation-ID", generate_correlation_id())
    set_correlation_id(cid)

    start = time.time()
    logger.info("Request started", path=request.url.path, method=request.method)

    response = await call_next(request)

    duration_ms = round((time.time() - start) * 1000, 2)
    logger.info("Request completed",
        path=request.url.path,
        status_code=response.status_code,
        duration_ms=duration_ms
    )

    response.headers["X-Correlation-ID"] = cid
    return response

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT
    }
    

app.include_router(research.router)

@app.on_event("startup")
async def startup_event():
    register_all_agents()
    from app.mcp.register_tools import register_all_tools
    register_all_tools()
    logger.info("Application started", app=settings.APP_NAME)
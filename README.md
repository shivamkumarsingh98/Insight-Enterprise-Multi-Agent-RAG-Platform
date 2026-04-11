  Insight: Enterprise Multi-Agent RAG Platform (Backend)
  Overview

Insight is an enterprise-grade Multi-Agent Retrieval-Augmented Generation (RAG) platform designed for deep research, semantic search, and intelligent knowledge synthesis.

It combines:

🧠 Multiple AI agents
🔎 Semantic search & reranking
📚 External research sources (Arxiv, Semantic Scholar)
🗂️ Long & short-term memory
⚙️ Modular and extensible architecture
🏗️ Architecture

The system follows a multi-agent orchestration model:
```text
 
                        ┌──────────────────────┐
                        │      User Query      │
                        └──────────┬───────────┘
                                   │
                                   ▼
                        ┌──────────────────────┐
                        │   API Layer (FastAPI)│
                        │   app/routes         │
                        └──────────┬───────────┘
                                   │
                                   ▼
                        ┌──────────────────────┐
                        │   Supervisor Agent   │
                        │   (Orchestrator)     │
                        └──────────┬───────────┘
                                   │
        ┌──────────────────────────┼──────────────────────────┐
        │                          │                          │
        ▼                          ▼                          ▼
┌───────────────┐        ┌───────────────┐        ┌───────────────┐
│ Classifier    │        │ Search Agent  │        │ Research Agent│
│ Agent         │        │               │        │ (Arxiv/Web)   │
└──────┬────────┘        └──────┬────────┘        └──────┬────────┘
       │                        │                        │
       ▼                        ▼                        ▼
┌───────────────┐        ┌───────────────┐        ┌───────────────┐
│ RAG Pipeline  │◄──────►│ Vector DB     │        │ External APIs │
│ (Chunking +   │        │ (ChromaDB)    │        │ (Arxiv, etc.) │
│ Embeddings)   │        └───────────────┘        └───────────────┘
└──────┬────────┘
       │
       ▼
┌───────────────┐
│ Reranker      │
│ Agent         │
└──────┬────────┘
       │
       ▼
┌───────────────┐
│ Summarizer    │
│ Agent         │
└──────┬────────┘
       │
       ▼
┌───────────────┐
│ Citation      │
│ Agent         │
└──────┬────────┘
       │
       ▼
┌───────────────┐
│ Memory System │
│ (Short + Long)│
└──────┬────────┘
       │
       ▼
┌───────────────┐
│ Final Response│
└───────────────┘
```

## 🏗️ Architecture
```text
app/
│
├── agents/              # Individual AI agents
│   ├── classifier_agent.py
│   ├── search_agent.py
│   ├── rerank_agent.py
│   ├── summarize_agent.py
│   ├── citation_agent.py
│   ├── deep_research_agent.py
│   └── workflow.py
│
├── core/                # Core utilities
│   ├── config.py
│   ├── llm.py
│   ├── logging.py
│   ├── security.py
│   └── circuit_breaker.py
│
├── services/            # External integrations
│   ├── arxiv.py
│   ├── semantic_scholar.py
│   ├── scraper.py
│   └── rag_pipeline.py
│
├── memory/              # Memory systems
│   ├── short_term.py
│   └── long_term.py
│
├── vector_db/           # Vector database (Chroma)
│   └── croma_db.py
│
├── data_ingestion/      # Data ingestion pipeline
│   └── ingest.py
│
├── routes/              # API endpoints
│   └── research.py
│
├── schemas/             # Request/response schemas
│   └── research.py
│
├── evaluation/          # Evaluation framework
├── governance/          # Audit & compliance
├── registry/            # Agent registration
├── supervisor/          # Orchestration logic
└── utils/               # Helper utilities

```

🧠 Key Features

🤖 Multi-Agent System
   Task-specific agents
   Modular & extendable
   Supervisor-driven orchestration

🔎 Advanced RAG Pipeline
    Chunking & embedding
    Vector search (ChromaDB)
    Reranking for relevance

📚 Research Integrations
    Arxiv papers
    Semantic Scholar
    Web scraping

🧠 Memory System
   Short-term conversational memory
   Long-term persistent memory

📊 Evaluation & Governance
   Response evaluation
   Audit logs
   Traceability


⚙️ Installation
1. Clone the repo

git clone https://github.com/shivamkumarsingh98/Insight-Enterprise-Multi-Agent-RAG-Platform.git
cd Backend

2. Create virtual environment
python -m venv .venv
source .venv/bin/activate   # Linux/Mac
.venv\Scripts\activate      # Windows

3. Install dependencies
pip install -r requirements.txt

🔑 Environment Variables
Create a .env file:
GROQ_API_KEY=your_api_key


▶️ Running the Server
uvicorn app.main:app --reload

📡 API Endpoints
🔍 Research Endpoint
POST /research

Request Body:
{
  "query": "Explain transformers in deep learning"
}

Response:
{
  "answer": "...",
  "sources": [...],
  "confidence": 0.92
}

🔄 Workflow
Query classification
Search (internal + external)
Chunk retrieval
Reranking
Summarization
Citation generation
Memory update
🧪 Evaluation
Stored in data/evaluations/
Tracks:
Accuracy
Relevance
Latency
🛡️ Security
API key management via .env
Circuit breaker for failures
Audit logging
📈 Future Improvements
UI dashboard
Streaming responses
Multi-modal support
Distributed agents
Fine-tuned models
🤝 Contributing
Fork repo
Create branch
Commit changes
Open PR
📜 License

MIT License

👨‍💻 Author

Shivam Singh

⭐ Final Note

This project is designed to be:

Scalable 🏗️
Modular 🧩
Enterprise-ready 🏢


# ClaimSight AI 🔍

> **An agentic AI system that replaces a manual data team** — takes natural language questions, routes them through 5 specialized agents, queries two insurance claim databases simultaneously, detects data integrity issues, and delivers structured business intelligence.

<br>

[![Python](https://img.shields.io/badge/Python-3.13-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![LangGraph](https://img.shields.io/badge/LangGraph-1.0-FF6B35?style=flat-square)](https://langchain-ai.github.io/langgraph/)
[![MCP](https://img.shields.io/badge/MCP-7_Tools-7C3AED?style=flat-square)](https://modelcontextprotocol.io)
[![Groq](https://img.shields.io/badge/Groq-Llama_3.3_70b-F55036?style=flat-square)](https://groq.com)
[![Streamlit](https://img.shields.io/badge/Streamlit-Live_Demo-FF4B4B?style=flat-square&logo=streamlit&logoColor=white)](https://your-deployment-link.streamlit.app)
[![FastAPI](https://img.shields.io/badge/FastAPI-REST_API-009688?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?style=flat-square&logo=docker&logoColor=white)](https://docker.com)
[![MLflow](https://img.shields.io/badge/MLflow-Tracked-0194E2?style=flat-square)](https://mlflow.org)

<br>

## 🚀 Live Demo

**[→ Launch ClaimSight AI](https://your-deployment-link.streamlit.app)**

> Ask in plain English. Get structured intelligence in seconds.

<br>

---

## 🏢 The Real Problem This Solves

In many companies, there is a dedicated data team whose entire job is:

1. Receive a data request from another team via email or Slack
2. Manually write a SQL query
3. Run it on the database
4. Export raw data as a CSV
5. Send it back — no summary, no insights, no comparison

**This takes hours. Sometimes days. And it scales with headcount.**

ClaimSight replaces this entire workflow with a 5-agent AI pipeline. Any team member types a question in plain English and gets a structured, accurate, insight-rich response in seconds — with no SQL knowledge required.

<br>

---

## 🎬 What It Does

```
"Find discrepancies between both claim databases"
                    ↓
┌─────────────────────────────────────────────────────────┐
│  Agent 1  →  Reads live schema from both databases      │
│  Agent 2  →  Builds precise SQL using schema context    │
│  Agent 3  →  Executes query on DB1 and DB2 in parallel  │
│  Agent 4  →  Compares results, flags 80 anomalies       │
│  Agent 5  →  Delivers structured analysis with memory   │
└─────────────────────────────────────────────────────────┘
                    ↓
  Ghost rows: 20   Orphan rows: 20   Mismatches: 40
  Financial impact: ₹47L discrepancy detected
  Recommended action: Immediate reconciliation required
```

<br>

---

## 🧠 System Architecture

```
User Query
    │
    ▼
┌─────────────────┐
│   Input Rail    │  ← blocks SQL injection, DROP/DELETE,
│   (Guardrail 1) │    prompt injection attempts
└────────┬────────┘
         │
    ▼
┌─────────────────┐
│ Schema Agent    │  ← MCP tool: inspect_schema()
│   (Agent 1)     │    discovers live table structure
└────────┬────────┘
         │
    ▼
┌─────────────────┐
│  Query Agent    │  ← MCP tools: validate_sql(), lookup_schema()
│   (Agent 2)     │    builds SQL from natural language
└────────┬────────┘
         │
    ▼
┌─────────────────┐
│   Query Rail    │  ← read-only enforcement, blocks mutations
│   (Guardrail 2) │    multi-statement attack prevention
└────────┬────────┘
         │
    ▼
┌─────────────────┐
│ Executor Agent  │  ← MCP tool: run_query()
│   (Agent 3)     │    runs SELECT on DB1 and DB2 simultaneously
└────────┬────────┘
         │
    ▼
┌─────────────────┐
│ Analyst Agent   │  ← MCP tools: diff_results(), flag_anomalies()
│   (Agent 4)     │    compares DBs, calculates financial impact
└────────┬────────┘
         │
    ▼
┌─────────────────┐
│   Chat Agent    │  ← full session memory, context-aware
│   (Agent 5)     │    answers follow-up questions
└────────┬────────┘
         │
    ▼
┌─────────────────┐
│  Output Rail    │  ← PII masking: email, phone, Aadhaar, PAN
│   (Guardrail 3) │    before any data reaches the user
└────────┬────────┘
         │
    ▼
  Clean, structured response with citations
```

<br>

---

## 📊 Benchmarks

| Metric | Value |
|--------|-------|
| Claims per database | 1,000 |
| Engineered discrepancies | 80 |
| Discrepancy types | 4 (ghost, orphan, status drift, amount drift) |
| MCP tools registered | 7 |
| Guardrail layers | 3 |
| Average response time | ~3s |
| MLflow runs tracked | 10+ |
| Supported query types | Natural language, any |

<br>

---

## 🛠 Tech Stack

| Layer | Technology | Why |
|-------|-----------|-----|
| Agent Orchestration | LangGraph | Industry-standard agent framework |
| Tool Protocol | MCP (Model Context Protocol) | Standardized tool calling, swap LLMs without touching tools |
| LLM | Groq — Llama 3.3 70b | Free, fast, no rate issues for demos |
| Databases | SQLite × 2 | Zero server setup, travels with repo |
| Guardrails | Custom 3-layer | Input → Query → Output safety chain |
| UI | Streamlit | 4-tab dashboard, chat + analytics |
| API | FastAPI | REST endpoint for machine-to-machine access |
| Experiment Tracking | MLflow | Every turn logged with params, metrics, artifacts |
| Containers | Docker + Compose | Production-ready, one command deploy |
| CI | GitHub branching | feature → dev → master workflow |

<br>

---

## 🗂 Project Structure

```
Claims_Insights_AI/
│
├── data/
│   ├── db1_claims_primary.sqlite    ← 1000 claims, clean
│   └── db2_claims_replica.sqlite    ← 1000 claims, 80 discrepancies
│
├── mcp_server/
│   └── server.py                    ← 7 MCP tools registered
│
├── agents/
│   ├── schema_agent.py              ← Agent 1: DB structure discovery
│   ├── query_agent.py               ← Agent 2: NL → SQL
│   ├── executor_agent.py            ← Agent 3: parallel DB execution
│   ├── analyst_agent.py             ← Agent 4: diff + anomaly detection
│   └── chat_agent.py                ← Agent 5: memory-aware responses
│
├── guardrails/
│   ├── input_rail.py                ← injection + prompt attack blocking
│   ├── query_rail.py                ← read-only SQL enforcement
│   └── output_rail.py               ← PII masking
│
├── core/
│   ├── database.py                  ← SQLite connection manager
│   ├── llm.py                       ← Groq client + LangChain wrapper
│   └── state.py                     ← LangGraph AgentState definition
│
├── api/
│   └── main.py                      ← FastAPI REST endpoint
│
├── ui/
│   └── app.py                       ← Streamlit 4-tab dashboard
│
├── graph.py                         ← LangGraph orchestration
├── generate_data.py                 ← DB generation + discrepancy engineering
├── eval.py                          ← MLflow batch evaluation
├── Dockerfile
└── docker-compose.yml
```

<br>

---

## ⚡ Run Locally

```bash
# 1. Clone
git clone https://github.com/themaheswar1/Claims_Insights_AI.git
cd Claims_Insights_AI

# 2. Environment
python -m venv venv
source venv/Scripts/activate  # Windows
# source venv/bin/activate    # Mac/Linux

# 3. Install
pip install -r requirements.txt

# 4. Configure
cp .env.example .env
# Add your GROQ_API_KEY to .env

# 5. Generate databases
python generate_data.py

# 6. Launch UI
streamlit run ui/app.py

# 7. (Optional) Launch API
python api/main.py

# 8. (Optional) Run MLflow evaluation
python eval.py
mlflow ui  # → http://localhost:5000
```

<br>

---

## 🐳 Run with Docker

```bash
docker compose up --build
# → http://localhost:8501
```

<br>

---

## 🔒 Security Model

**Three-layer guardrail chain — every request passes through all three:**

| Layer | What it blocks |
|-------|---------------|
| Input rail | SQL keywords in natural language, prompt injection, `ignore instructions` attacks |
| Query rail | Non-SELECT statements, DROP/DELETE/UPDATE, multi-statement injection, ALTER |
| Output rail | Email addresses, phone numbers, Aadhaar-format IDs, PAN card numbers |

```bash
# Try it yourself
> "DROP TABLE claims"
⚠️ Request blocked: Query contains restricted keyword 'drop'.
   Only data retrieval requests are allowed.
```

<br>

---

## 🔌 REST API

```bash
# Health check
GET /health

# Query the system
POST /query
{
  "query": "Show all pending claims above 1 lakh",
  "session_id": "optional-for-memory"
}

# Response
{
  "response": "...",
  "sql_query": "SELECT ...",
  "db1_rows": 47,
  "db2_rows": 44,
  "anomalies": 3,
  "agent_path": ["schema_agent", "query_agent", ...],
  "time_taken": 2.847
}
```

Full interactive docs at `/docs` (Swagger UI).

<br>

---

## 📈 MLflow Tracking

Every conversation turn is logged as an MLflow experiment run:

```
Params:   query, agent_path, blocked, session_id
Metrics:  db1_rows, db2_rows, anomalies, response_time, agents_used
Artifacts: full conversation log with SQL and response
```

```bash
python eval.py   # run 10-query benchmark
mlflow ui        # view at http://localhost:5000
```

<br>

---

## 💡 Sample Queries

```
"Show me all pending claims"
"Find discrepancies between both databases"
"Which region has the most claims?"
"Show settled claims above 2 lakhs"
"How many approved claims are there?"
"Compare claim amounts between DB1 and DB2"
"Show claims by type with average amount"
"Find claims that exist in DB1 but not DB2"
```

<br>

---

## 🗺 Roadmap

- [x] 5-agent LangGraph pipeline
- [x] MCP server with 7 tools
- [x] 3-layer guardrail system
- [x] Streamlit 4-tab dashboard
- [x] FastAPI REST endpoint
- [x] MLflow experiment tracking
- [x] Docker containerization
- [x] Deploy to Streamlit Cloud
- [ ] Scheduled discrepancy reports via email
- [ ] Export diff report as PDF
- [ ] Multi-database support beyond SQLite
- [ ] Role-based access control
- [ ] Slack/Teams integration for alerts

<br>

---

## 👨‍💻 Author

Built by **Mahesh** — failed multiple times building this, shipped it anyway.

> *"The best way to learn AI engineering is to replace something real."*

[![GitHub](https://img.shields.io/badge/GitHub-themaheswar1-181717?style=flat-square&logo=github)](https://github.com/themaheswar1)


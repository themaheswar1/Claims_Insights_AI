<div align="center">

# ClaimSight AI 🔍

### *An agentic AI system that replaced a manual data team*

**Natural language → 5 specialized agents → dual database intelligence → structured business insights**

<br>

[![Python](https://img.shields.io/badge/Python-3.13-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![LangGraph](https://img.shields.io/badge/LangGraph-Orchestration-FF6B35?style=flat-square)](https://langchain-ai.github.io/langgraph/)
[![MCP](https://img.shields.io/badge/MCP-7_Tools-7C3AED?style=flat-square)](https://modelcontextprotocol.io)
[![Groq](https://img.shields.io/badge/Groq-Llama_3.3_70b-F55036?style=flat-square)](https://groq.com)
[![FastAPI](https://img.shields.io/badge/FastAPI-REST_API-009688?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Docker](https://img.shields.io/badge/Docker-Containerized-2496ED?style=flat-square&logo=docker&logoColor=white)](https://docker.com)
[![AWS](https://img.shields.io/badge/AWS-Elastic_Beanstalk-FF9900?style=flat-square&logo=amazonaws&logoColor=white)](https://aws.amazon.com/elasticbeanstalk/)
[![MLflow](https://img.shields.io/badge/MLflow-Experiment_Tracking-0194E2?style=flat-square)](https://mlflow.org)

<br>

> 🚀 **Deployed on AWS Elastic Beanstalk** — EC2 t3.small · ap-south-1 Mumbai · Application Load Balancer · Auto Scaling
>
> **[→ Live Demo](http://claimsight-production.eba-am2fzpmk.ap-south-1.elasticbeanstalk.com)**

</div>

---

## The Problem This Solves

In many companies, there is a dedicated team whose entire job is to manually serve data requests:

```
Other team asks → data team writes SQL → runs query → exports CSV → sends raw data
                                                                    (no summary, no insights)
Hours or days. Scales with headcount. Breaks when team is unavailable.
```

**ClaimSight replaces this entire workflow with a 5-agent AI pipeline.**

Any team member types a question in plain English. The system routes it through 5 specialized agents, queries two insurance claim databases simultaneously, detects data integrity issues, and delivers structured business intelligence — in seconds.

---

## Architecture

```
User Query
    │
    ▼
┌──────────────────┐
│   Input Rail     │  blocks SQL injection · prompt injection · forbidden keywords
└────────┬─────────┘
         │
    ▼
┌──────────────────┐
│  Agent 1         │  MCP tools: inspect_schema() · list_tables()
│  Schema Agent    │  discovers live table structure from both databases
└────────┬─────────┘
         │
    ▼
┌──────────────────┐
│  Agent 2         │  MCP tools: validate_sql() · lookup_schema() · explain_query()
│  Query Agent     │  converts natural language → precise SQL using live schema context
└────────┬─────────┘
         │
    ▼
┌──────────────────┐
│   Query Rail     │  read-only enforcement · blocks mutations · multi-statement prevention
└────────┬─────────┘
         │
    ▼
┌──────────────────┐
│  Agent 3         │  MCP tool: run_query()
│  Executor Agent  │  runs SELECT on DB1 and DB2 simultaneously · PII masking applied
└────────┬─────────┘
         │
    ▼
┌──────────────────┐
│  Agent 4         │  MCP tools: diff_results() · flag_anomalies() · generate_summary()
│  Analyst Agent   │  cross-DB comparison · anomaly detection · financial impact analysis
└────────┬─────────┘
         │
    ▼
┌──────────────────┐
│  Agent 5         │  full session memory · context-aware follow-up handling
│  Chat Agent      │  answers questions about the data with citations
└────────┬─────────┘
         │
    ▼
┌──────────────────┐
│   Output Rail    │  masks email · phone · Aadhaar · PAN before response reaches user
└──────────────────┘
```

---

## What Makes This Different

| Feature | Most Projects | ClaimSight |
|---------|--------------|------------|
| Query method | Hardcoded SQL | Natural language → SQL via LLM |
| Database coverage | Single DB | Two DBs simultaneously |
| Data comparison | Manual | Automated diff engine |
| Security | None | 3-layer guardrail chain |
| Tool protocol | Direct function calls | MCP (Model Context Protocol) |
| API access | UI only | REST endpoint for machine-to-machine |
| Deployment | Local / Streamlit | AWS Elastic Beanstalk + Docker |
| Observability | None | MLflow experiment tracking |

---

## Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| Agent Orchestration | LangGraph | StateGraph with conditional routing |
| Tool Protocol | MCP server | 7 registered tools, standardized calling |
| LLM | Groq — Llama 3.3 70b | Fast inference, natural language understanding |
| Databases | SQLite × 2 | Dual claims databases with engineered discrepancies |
| Guardrails | Custom 3-layer | Input → Query → Output safety chain |
| UI | Streamlit | 4-tab dashboard: Chat, Analytics, Diff View, History |
| API | FastAPI | REST endpoint: `/query`, `/health`, `/schema`, `/stats` |
| Tracking | MLflow | Params, metrics, artifacts per conversation turn |
| Containers | Docker + Compose | Production-ready, single command deploy |
| Cloud | AWS Elastic Beanstalk | EC2 t3.small, ALB, Auto Scaling, CloudWatch |
| CI/CD | GitHub branching | feature → dev → master workflow, 11 commits |

---

## Benchmarks

| Metric | Value |
|--------|-------|
| Claims per database | 1,000 |
| Engineered discrepancies | 80 |
| Discrepancy types | Ghost rows · Orphan rows · Status drift · Amount drift |
| MCP tools registered | 7 |
| Guardrail layers | 3 |
| Average response time | ~3 seconds |
| MLflow runs tracked | 10+ |
| AWS region | ap-south-1 (Mumbai) |

---

## Security Model

Three guardrail layers — every request passes through all three before any data is returned.

```
Layer 1 — Input Rail
  Blocks: DROP, DELETE, INSERT, UPDATE, TRUNCATE in natural language
  Blocks: Prompt injection — "ignore previous instructions", "act as", "jailbreak"
  Blocks: Queries over 2000 characters (prompt stuffing prevention)

Layer 2 — Query Rail  
  Blocks: Any non-SELECT SQL statement
  Blocks: Multi-statement injection (chained semicolons)
  Blocks: SQL comment injection (--, /*, */)
  Allows: Only pure SELECT queries

Layer 3 — Output Rail
  Masks: Email addresses → [EMAIL REDACTED]
  Masks: Phone numbers → [PHONE REDACTED]
  Masks: Aadhaar-format IDs → [ID REDACTED]
  Masks: PAN card numbers → [PAN REDACTED]
```

**Try it yourself:**
```
Query: "DROP TABLE claims"
Response: ⚠️ Request blocked: Query contains restricted keyword 'drop'.
          Only data retrieval requests are allowed.
```

---

## MCP Tools

All agent tool calls go through the MCP server — standardized, swappable, independently testable.

| Tool | Agent | Purpose |
|------|-------|---------|
| `list_tables()` | Schema Agent | Discovers all tables in a database |
| `inspect_schema()` | Schema Agent | Returns human-readable schema description |
| `validate_sql()` | Query Agent | Syntax and safety validation before execution |
| `lookup_schema()` | Query Agent | Live schema lookup during query building |
| `run_query()` | Executor Agent | Safe SELECT execution on DB1 or DB2 |
| `diff_results()` | Analyst Agent | Cross-database comparison engine |
| `database_stats()` | Health check | Row counts across all tables, both DBs |

---

## REST API

```bash
# Health check
GET /health
→ { "status": "healthy", "databases": {...}, "graph": "loaded" }

# Query the system
POST /query
{
  "query": "Show all pending claims above 1 lakh",
  "session_id": "optional-uuid-for-memory"
}
→ {
    "response": "There are 47 pending claims above ₹1 lakh...",
    "sql_query": "SELECT claim_id, status, claim_amount FROM claims WHERE...",
    "db1_rows": 47,
    "db2_rows": 44,
    "anomalies": 3,
    "agent_path": ["schema_agent", "query_agent", "executor_agent", "analyst_agent", "chat_agent"],
    "time_taken": 2.847
  }

# Live schema
GET /schema
→ full table structure for both databases

# Database stats
GET /stats
→ row counts per table per database
```

Full interactive docs at `/docs` (Swagger UI).

---

## Project Structure

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
│   ├── schema_agent.py              ← Agent 1: live schema discovery
│   ├── query_agent.py               ← Agent 2: NL → SQL with validation
│   ├── executor_agent.py            ← Agent 3: parallel DB execution
│   ├── analyst_agent.py             ← Agent 4: diff + anomaly detection
│   └── chat_agent.py                ← Agent 5: memory-aware responses
│
├── guardrails/
│   ├── input_rail.py                ← pre-agent safety check
│   ├── query_rail.py                ← read-only SQL enforcement
│   └── output_rail.py               ← PII masking
│
├── core/
│   ├── database.py                  ← SQLite connection manager
│   ├── llm.py                       ← Groq client + LangChain wrapper
│   └── state.py                     ← LangGraph AgentState TypedDict
│
├── api/main.py                      ← FastAPI REST endpoint
├── ui/app.py                        ← Streamlit 4-tab dashboard
├── graph.py                         ← LangGraph orchestration
├── generate_data.py                 ← DB generation + discrepancy engineering
├── eval.py                          ← MLflow batch evaluation
├── Dockerfile
└── docker-compose.yml
```

---

## Run Locally

```bash
# 1. Clone
git clone https://github.com/themaheswar1/Claims_Insights_AI.git
cd Claims_Insights_AI

# 2. Environment
python -m venv venv
source venv/Scripts/activate   # Windows
# source venv/bin/activate     # Mac/Linux

# 3. Install
pip install -r requirements.txt

# 4. Configure
cp .env.example .env
# Add your GROQ_API_KEY to .env

# 5. Generate databases
python generate_data.py

# 6. Launch
streamlit run ui/app.py
```

---

## Run with Docker

```bash
docker compose up --build
# → http://localhost:8501
```

---

## AWS Deployment

```bash
# Install EB CLI
pip install awsebcli

# Configure AWS credentials
aws configure

# Initialize
eb init

# Deploy
eb create claimsight-production --instance-type t3.small \
  --envvars GROQ_API_KEY=your_key_here

# Open
eb open
```

---

## MLflow Tracking

Every conversation turn is logged as an MLflow experiment run.

```bash
python eval.py    # run 10-query benchmark suite
mlflow ui         # → http://localhost:5000
```

Logged per turn: query, SQL, agent path, DB row counts, anomalies, response time, blocked status, full conversation artifact.

---

## Sample Queries

```
"Show me all pending claims"
"Find discrepancies between both databases"
"Which region has the most claims?"
"Show settled claims above 2 lakhs"
"Compare claim amounts between DB1 and DB2"
"How many approved claims are there?"
"Find claims that exist in DB1 but not DB2"
"Show claims by type with average settlement amount"
```

---

## Roadmap

- [x] 5-agent LangGraph pipeline
- [x] MCP server with 7 tools
- [x] 3-layer guardrail system
- [x] Streamlit 4-tab dashboard
- [x] FastAPI REST endpoint
- [x] MLflow experiment tracking
- [x] Docker containerization
- [x] AWS Elastic Beanstalk deployment
- [ ] Scheduled discrepancy reports via email alerts
- [ ] Export diff report as PDF
- [ ] Role-based access control
- [ ] Support for PostgreSQL and MySQL
- [ ] Slack integration for anomaly notifications

---

<div align="center">

Built by **Mahesh** — failed multiple times, shipped it anyway.

*"The best projects come from watching real teams struggle with real problems."*

[![GitHub](https://img.shields.io/badge/GitHub-themaheswar1-181717?style=flat-square&logo=github)](https://github.com/themaheswar1)

</div>

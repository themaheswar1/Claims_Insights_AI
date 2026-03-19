import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import uuid
import time
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional

from graph import build_graph, run_turn
from core.database import get_db_stats, get_schema

# Load graph once at startup 
graph = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global graph
    print("Starting ClaimSight API...")
    graph = build_graph()
    print("✅ Graph ready.")
    yield
    print("Shutting down ClaimSight API...")

# App Setup 
app = FastAPI(
    title       = "ClaimSight AI API",
    description = "Agentic AI system for Insurance claims Insights Intelligence",
    version     = "1.0.0",
    lifespan    = lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins     = ["*"],
    allow_credentials = True,
    allow_methods     = ["*"],
    allow_headers     = ["*"],
)

# Request / Response Models 
class QueryRequest(BaseModel):
    query:      str
    session_id: Optional[str] = None
    memory:     Optional[list] = []

class QueryResponse(BaseModel):
    session_id:   str
    query:        str
    sql_query:    str
    response:     str
    db1_rows:     int
    db2_rows:     int
    anomalies:    int
    blocked:      bool
    block_reason: str
    agent_path:   list
    time_taken:   float

# Routes 
@app.get("/")
def root():
    return {
        "name":    "ClaimSight AI API",
        "version": "1.0.0",
        "status":  "running",
        "docs":    "/docs",
    }

@app.get("/health")
def health():
    stats = {
        "db1": get_db_stats("db1"),
        "db2": get_db_stats("db2"),
    }
    return {
        "status":    "healthy",
        "databases": stats,
        "graph":     "loaded" if graph else "not loaded",
    }

@app.get("/schema")
def schema():
    return {
        "db1": get_schema("db1"),
        "db2": get_schema("db2"),
    }

@app.post("/query", response_model=QueryResponse)
def query(request: QueryRequest):
    global graph

    if not graph:
        raise HTTPException(status_code=503, detail="Graph not initialized.")

    session_id = request.session_id or str(uuid.uuid4())

    start  = time.time()
    result = run_turn(
        user_query = request.query,
        memory     = request.memory or [],
        session_id = session_id,
        graph      = graph,
    )
    elapsed = round(time.time() - start, 3)

    return QueryResponse(
        session_id   = session_id,
        query        = request.query,
        sql_query    = result.get("sql_query", ""),
        response     = result.get("response", ""),
        db1_rows     = len(result.get("db1_results", [])),
        db2_rows     = len(result.get("db2_results", [])),
        anomalies    = len(result.get("anomalies", [])),
        blocked      = result.get("blocked", False),
        block_reason = result.get("block_reason", ""),
        agent_path   = result.get("agent_path", []),
        time_taken   = elapsed,
    )

@app.get("/stats")
def stats():
    return {
        "db1": get_db_stats("db1"),
        "db2": get_db_stats("db2"),
    }

# main
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api.main:app", host="0.0.0.0", port=8000, reload=False)
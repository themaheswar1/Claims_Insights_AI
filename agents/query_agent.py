import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.state import AgentState
from core.llm import get_chat_llm
from mcp_server.server import validate_sql, inspect_schema
from guardrails.query_rail import check_query
from langchain_core.messages import SystemMessage, HumanMessage

SYSTEM_PROMPT = """You are a SQL Query Builder Agent for ClaimSight.
Your job is to convert natural language questions into precise SQLite SELECT queries.

Rules:
- ONLY write SELECT queries. Never write anything else.
- Use EXACT column names from the schema — case sensitive.
- Status values are UPPERCASE: 'PENDING', 'APPROVED', 'REJECTED', 'SETTLED', 'UNDER_REVIEW'
- Always add LIMIT 100 unless user asks for counts or aggregations.
- For comparison or discrepancy questions, write:
  SELECT claim_id, status, claim_amount FROM claims LIMIT 100
- Return ONLY the raw SQL — no explanation, no markdown, no backticks, no comments.
- Start your response with SELECT and nothing else.
- If the question cannot be answered with SQL, return exactly: SELECT claim_id, status, claim_amount FROM claims LIMIT 100"""

def run_query_agent(state: AgentState) -> AgentState:
    print("  [Agent 2] Query Builder running...")

    user_query = state["user_query"]
    schema     = inspect_schema("db1")

    llm = get_chat_llm(temperature=0.0)

    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=f"""
Database Schema:
{schema}

User Question: {user_query}

Write the SQL query:
""")
    ]

    response    = llm.invoke(messages)
    sql_query   = response.content.strip()

    # remove markdown if model added it
    if sql_query.startswith("```"):
        lines     = sql_query.split("\n")
        sql_query = "\n".join(
            line for line in lines
            if not line.startswith("```")
        ).strip()

    # validate with MCP tool
    mcp_validation = validate_sql(sql_query)

    # validate with query rail
    rail_check = check_query(sql_query)

    if not mcp_validation["valid"] or not rail_check["allowed"]:
        reason = mcp_validation.get("reason") or rail_check.get("reason")
        print(f"  [Agent 2] Query blocked: {reason}")
        return {
            **state,
            "sql_query":   sql_query,
            "query_valid": False,
            "query_error": reason,
            "blocked":     True,
            "block_reason": reason,
            "agent_path":  state.get("agent_path", []) + ["query_agent"],
        }

    print(f"  [Agent 2] Query built: {sql_query[:60]}...")

    return {
        **state,
        "sql_query":   sql_query,
        "query_valid": True,
        "query_error": "",
        "agent_path":  state.get("agent_path", []) + ["query_agent"],
    }
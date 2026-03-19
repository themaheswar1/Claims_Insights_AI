import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.state import AgentState
from core.llm import get_chat_llm
from mcp_server.server import inspect_schema, list_tables
from langchain_core.messages import SystemMessage, HumanMessage

SYSTEM_PROMPT = """You are a Database Schema Discovery Agent for ClaimSight.
Your job is to examine both databases and understand their structure completely.
You must identify all tables, columns, data types, and relationships.
Be precise and thorough — other agents depend on your output to build correct queries."""

def run_schema_agent(state: AgentState) -> AgentState:
    print("  [Agent 1] Schema Discovery running...")

    # use MCP tools to get schema from both DBs
    schema_db1 = list_tables("db1")
    schema_db2 = list_tables("db2")

    # get human readable description
    description_db1 = inspect_schema("db1")
    description_db2 = inspect_schema("db2")

    llm = get_chat_llm(temperature=0.0)

    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=f"""
Analyze these two database schemas and confirm you understand them:

DB1 (Claims Primary):
{description_db1}

DB2 (Claims Replica):
{description_db2}

Confirm the key tables and columns available for querying.
Keep response under 100 words.
""")
    ]

    response = llm.invoke(messages)

    print(f"  [Agent 1] Schema loaded — "
          f"DB1: {list(schema_db1.keys())}, "
          f"DB2: {list(schema_db2.keys())}")

    return {
        **state,
        "schema_db1": schema_db1,
        "schema_db2": schema_db2,
        "agent_path": state.get("agent_path", []) + ["schema_agent"],
    }
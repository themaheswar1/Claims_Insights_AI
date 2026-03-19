import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.state import AgentState
from mcp_server.server import run_query
from guardrails.output_rail import mask_pii_in_rows

def run_executor_agent(state: AgentState) -> AgentState:
    print("  [Agent 3] DB Executor running...")

    if not state.get("query_valid", False):
        print("  [Agent 3] Skipping — query was blocked.")
        return {
            **state,
            "agent_path": state.get("agent_path", []) + ["executor_agent"],
        }

    sql_query = state["sql_query"]

    # run on DB1
    result_db1 = run_query(sql_query, "db1")
    # run on DB2
    result_db2 = run_query(sql_query, "db2")

    if result_db1.get("error"):
        print(f"  [Agent 3] DB1 error: {result_db1['error']}")
        return {
            **state,
            "db1_results":     [],
            "db2_results":     [],
            "execution_error": result_db1["error"],
            "agent_path":      state.get("agent_path", []) + ["executor_agent"],
        }

    if result_db2.get("error"):
        print(f"  [Agent 3] DB2 error: {result_db2['error']}")
        return {
            **state,
            "db1_results":     [],
            "db2_results":     [],
            "execution_error": result_db2["error"],
            "agent_path":      state.get("agent_path", []) + ["executor_agent"],
        }

    # mask PII before storing results
    db1_rows = mask_pii_in_rows(result_db1["rows"])
    db2_rows = mask_pii_in_rows(result_db2["rows"])

    print(f"  [Agent 3] DB1: {len(db1_rows)} rows | "
          f"DB2: {len(db2_rows)} rows")

    return {
        **state,
        "db1_results":     db1_rows,
        "db2_results":     db2_rows,
        "execution_error": "",
        "agent_path":      state.get("agent_path", []) + ["executor_agent"],
    }
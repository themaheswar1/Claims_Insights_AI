import os
import uuid
from typing import Literal
from langgraph.graph import StateGraph, END

from core.state import AgentState
from agents.schema_agent   import run_schema_agent
from agents.query_agent    import run_query_agent
from agents.executor_agent import run_executor_agent
from agents.analyst_agent  import run_analyst_agent
from agents.chat_agent     import run_chat_agent
from guardrails.input_rail import check_input

# ── Router ────────────────────────────────────────────────────────────────────
def route_after_query(state: AgentState) -> Literal["executor_agent", "chat_agent"]:
    """
    After query builder runs:
    - If query was blocked → skip to chat agent (will show block message)
    - If query is valid    → proceed to executor
    """
    if state.get("blocked", False):
        return "chat_agent"
    return "executor_agent"

# ── Build Graph ───────────────────────────────────────────────────────────────
def build_graph():
    graph = StateGraph(AgentState)

    # add all 5 agent nodes
    graph.add_node("schema_agent",   run_schema_agent)
    graph.add_node("query_agent",    run_query_agent)
    graph.add_node("executor_agent", run_executor_agent)
    graph.add_node("analyst_agent",  run_analyst_agent)
    graph.add_node("chat_agent",     run_chat_agent)

    # entry point — always starts with schema discovery
    graph.set_entry_point("schema_agent")

    # schema → query builder
    graph.add_edge("schema_agent", "query_agent")

    # query builder → router decides next
    graph.add_conditional_edges(
        "query_agent",
        route_after_query,
        {
            "executor_agent": "executor_agent",
            "chat_agent":     "chat_agent",
        }
    )

    # executor → analyst
    graph.add_edge("executor_agent", "analyst_agent")

    # analyst → chat
    graph.add_edge("analyst_agent", "chat_agent")

    # chat → end
    graph.add_edge("chat_agent", END)

    return graph.compile()

# ── Run One Turn ──────────────────────────────────────────────────────────────
def run_turn(
    user_query:  str,
    memory:      list = None,
    session_id:  str  = None,
    graph              = None,
) -> AgentState:
    """
    Runs one full pipeline turn for a user query.
    Returns the final state after all agents have run.
    """
    # check input guardrail first
    input_check = check_input(user_query)
    if not input_check["allowed"]:
        return {
            "user_query":      user_query,
            "schema_db1":      {},
            "schema_db2":      {},
            "sql_query":       "",
            "query_valid":     False,
            "query_error":     input_check["reason"],
            "db1_results":     [],
            "db2_results":     [],
            "execution_error": "",
            "diff_report":     {},
            "anomalies":       [],
            "summary":         "",
            "response":        f"⚠️ Request blocked: {input_check['reason']}",
            "memory":          memory or [],
            "blocked":         True,
            "block_reason":    input_check["reason"],
            "agent_path":      ["input_rail"],
            "session_id":      session_id or str(uuid.uuid4()),
        }

    # build initial state
    initial_state = AgentState(
        user_query      = user_query,
        schema_db1      = {},
        schema_db2      = {},
        sql_query       = "",
        query_valid     = False,
        query_error     = "",
        db1_results     = [],
        db2_results     = [],
        execution_error = "",
        diff_report     = {},
        anomalies       = [],
        summary         = "",
        response        = "",
        memory          = memory or [],
        blocked         = False,
        block_reason    = "",
        agent_path      = [],
        session_id      = session_id or str(uuid.uuid4()),
    )

    return graph.invoke(initial_state)

# ── Entry Point — full pipeline test ─────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 55)
    print("  ClaimSight — Full Pipeline Test")
    print("=" * 55)

    print("\nBuilding graph...")
    g = build_graph()
    print("✅ Graph compiled successfully\n")

    # Test 1 — normal query
    print("─" * 55)
    print("Test 1: Normal query")
    print("─" * 55)
    result = run_turn(
        user_query = "Show me all pending claims",
        graph      = g,
    )
    print(f"\nAgent path : {result['agent_path']}")
    print(f"SQL query  : {result['sql_query']}")
    print(f"DB1 rows   : {len(result['db1_results'])}")
    print(f"DB2 rows   : {len(result['db2_results'])}")
    print(f"Response   :\n{result['response']}")

    # Test 2 — blocked query
    print("\n" + "─" * 55)
    print("Test 2: Blocked query")
    print("─" * 55)
    result2 = run_turn(
        user_query = "DROP TABLE claims",
        graph      = g,
    )
    print(f"\nBlocked    : {result2['blocked']}")
    print(f"Reason     : {result2['block_reason']}")
    print(f"Response   : {result2['response']}")

    # Test 3 — comparison query
    print("\n" + "─" * 55)
    print("Test 3: Comparison query")
    print("─" * 55)
    result3 = run_turn(
        user_query = "Compare claims data between both databases and show discrepancies",
        graph      = g,
    )
    print(f"\nAgent path : {result3['agent_path']}")
    print(f"Anomalies  : {len(result3['anomalies'])}")
    print(f"Summary    :\n{result3['summary']}")

    print("\n" + "=" * 55)
    print("  Full pipeline test complete.")
    print("=" * 55)
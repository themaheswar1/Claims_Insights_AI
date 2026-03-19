import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.state import AgentState
from core.llm import get_chat_llm
from mcp_server.server import diff_results
from langchain_core.messages import SystemMessage, HumanMessage

SYSTEM_PROMPT = """You are a Senior Data Analyst Agent for ClaimSight.
Your job is to compare data from two insurance claim databases and identify:
- Missing records (exists in one DB but not the other)
- Value mismatches (same record, different values)
- Data integrity issues
- Patterns in the discrepancies

Be specific — mention claim IDs, amounts, statuses.
Use clear business language. Be concise but thorough.
Format your response with clear sections."""

def run_analyst_agent(state: AgentState) -> AgentState:
    print("  [Agent 4] Analyst running...")

    db1_results = state.get("db1_results", [])
    db2_results = state.get("db2_results", [])
    sql_query   = state.get("sql_query", "")

    if not db1_results and not db2_results:
        return {
            **state,
            "diff_report": {},
            "anomalies":   [],
            "summary":     "No data available for analysis.",
            "agent_path":  state.get("agent_path", []) + ["analyst_agent"],
        }

    # use MCP diff tool
    diff = diff_results(sql_query, key_col="claim_id") \
        if "claim_id" in sql_query or "claims" in sql_query \
        else {"ghost_rows": [], "orphan_rows": [], "mismatches": [],
              "summary": {"total_issues": 0}}

    # build context for LLM
    diff_context = f"""
DB1 returned {len(db1_results)} rows.
DB2 returned {len(db2_results)} rows.

Discrepancies found:
- Ghost rows (in DB1, missing from DB2): {diff.get('summary', {}).get('ghost_count', 0)}
- Orphan rows (in DB2, missing from DB1): {diff.get('summary', {}).get('orphan_count', 0)}
- Value mismatches: {diff.get('summary', {}).get('mismatch_count', 0)}
- Total issues: {diff.get('summary', {}).get('total_issues', 0)}

Sample mismatches (first 3):
{diff.get('mismatches', [])[:3]}

Sample ghost rows (first 3):
{diff.get('ghost_rows', [])[:3]}

Sample orphan rows (first 3):
{diff.get('orphan_rows', [])[:3]}
"""

    llm = get_chat_llm(temperature=0.3)

    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=f"""
User asked: {state['user_query']}

Analysis data:
{diff_context}

Provide a clear analysis report with:
1. Summary of findings
2. Key discrepancies
3. Business impact
4. Recommended action
""")
    ]

    response = llm.invoke(messages)
    summary  = response.content.strip()

    anomalies = (
        [{"type": "ghost",    "data": r} for r in diff.get("ghost_rows",  [])[:10]] +
        [{"type": "orphan",   "data": r} for r in diff.get("orphan_rows", [])[:10]] +
        [{"type": "mismatch", "data": r} for r in diff.get("mismatches",  [])[:10]]
    )

    print(f"  [Agent 4] Analysis complete — "
          f"{diff.get('summary', {}).get('total_issues', 0)} issues found")

    return {
        **state,
        "diff_report": diff,
        "anomalies":   anomalies,
        "summary":     summary,
        "agent_path":  state.get("agent_path", []) + ["analyst_agent"],
    }
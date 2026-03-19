import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.state import AgentState
from core.llm import get_chat_llm
from guardrails.output_rail import check_output
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

SYSTEM_PROMPT = """You are ClaimSight's intelligent data assistant.
You have access to insurance claims data from two databases and their analysis.

Your job:
- Answer user questions accurately using the data and analysis provided
- Be specific — cite claim IDs, amounts, counts, statuses
- Be concise — answer directly, no filler
- If asked about discrepancies, refer to the analyst's findings
- If data is insufficient, say so clearly

You have full memory of this session — refer to previous questions if relevant."""

def run_chat_agent(state: AgentState) -> AgentState:
    print("  [Agent 5] Chat Agent running...")

    # if blocked by guardrail
    if state.get("blocked", False):
        return {
            **state,
            "response":   f"⚠️ Request blocked: {state.get('block_reason', 'Security policy violation.')}",
            "agent_path": state.get("agent_path", []) + ["chat_agent"],
        }

    user_query  = state["user_query"]
    db1_results = state.get("db1_results", [])
    db2_results = state.get("db2_results", [])
    summary     = state.get("summary", "")
    memory      = state.get("memory", [])
    sql_query   = state.get("sql_query", "")

    # build context
    context = f"""
User Question: {user_query}

SQL Query Used: {sql_query}

DB1 Results ({len(db1_results)} rows):
{db1_results[:5]}

DB2 Results ({len(db2_results)} rows):
{db2_results[:5]}

Analyst Summary:
{summary}
"""

    # build messages with memory
    messages = [SystemMessage(content=SYSTEM_PROMPT)]

    # add last 6 memory turns
    for turn in memory[-6:]:
        if turn["role"] == "user":
            messages.append(HumanMessage(content=turn["content"]))
        else:
            messages.append(AIMessage(content=turn["content"]))

    messages.append(HumanMessage(content=context))

    llm      = get_chat_llm(temperature=0.3)
    response = llm.invoke(messages)
    raw_text = response.content.strip()

    # output rail — mask PII
    output   = check_output(raw_text, db1_results)
    clean    = output["clean_response"]

    # update memory
    updated_memory = memory + [
        {"role": "user",      "content": user_query},
        {"role": "assistant", "content": clean},
    ]

    print(f"  [Agent 5] Response ready — {len(clean)} chars")

    return {
        **state,
        "response":   clean,
        "memory":     updated_memory,
        "agent_path": state.get("agent_path", []) + ["chat_agent"],
    }
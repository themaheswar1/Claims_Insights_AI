import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import uuid
import streamlit as st
import pandas as pd
from graph import build_graph, run_turn
from core.database import get_db_stats, execute_query

# ── Page Config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title = "ClaimSight Intelligence AI",
    page_icon  = "🔍",
    layout     = "wide",
)

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&display=swap');
* { font-family: 'Inter', sans-serif !important; }

.stApp { background-color: #0a0a0f; }
.block-container { padding-top: 1.5rem; }

.hero {
    background: #0f0f1a;
    border: 1px solid #1e1e2e;
    border-radius: 12px;
    padding: 24px 32px;
    margin-bottom: 24px;
}
.hero h1 {
    font-size: 24px;
    font-weight: 600;
    color: #ffffff;
    margin: 0 0 4px 0;
}
.hero p {
    font-size: 13px;
    color: #555;
    margin: 0;
}
.metric-card {
    background: #0f0f1a;
    border: 1px solid #1e1e2e;
    border-radius: 10px;
    padding: 16px 20px;
    text-align: center;
}
.metric-value {
    font-size: 28px;
    font-weight: 600;
    color: #7c6bff;
}
.metric-label {
    font-size: 11px;
    color: #555;
    text-transform: uppercase;
    letter-spacing: 1px;
}
.agent-pill {
    display: inline-block;
    padding: 2px 10px;
    border-radius: 20px;
    font-size: 11px;
    font-weight: 500;
    margin-right: 4px;
}
.pill-schema   { background: #1a1a3a; color: #7c6bff; }
.pill-query    { background: #0d2035; color: #4a9eca; }
.pill-executor { background: #0d2a1a; color: #4aca7e; }
.pill-analyst  { background: #2a1a00; color: #caaa4a; }
.pill-chat     { background: #2a0d0d; color: #ca4a4a; }
.pill-blocked  { background: #3a0d0d; color: #ff4a4a; }

.diff-ghost   { background: #1a0d0d; border-left: 3px solid #ca4a4a;
                padding: 8px 12px; border-radius: 0 6px 6px 0;
                font-size: 12px; margin-bottom: 4px; }
.diff-orphan  { background: #0d1a0d; border-left: 3px solid #4aca7e;
                padding: 8px 12px; border-radius: 0 6px 6px 0;
                font-size: 12px; margin-bottom: 4px; }
.diff-mismatch{ background: #1a1a0d; border-left: 3px solid #caaa4a;
                padding: 8px 12px; border-radius: 0 6px 6px 0;
                font-size: 12px; margin-bottom: 4px; }

.sql-box {
    background: #0d0d1a;
    border: 1px solid #1e1e2e;
    border-radius: 8px;
    padding: 12px 16px;
    font-family: monospace;
    font-size: 13px;
    color: #7c6bff;
    margin: 8px 0;
}
section[data-testid="stSidebar"] {
    background: #0a0a0f !important;
    border-right: 1px solid #1e1e2e !important;
}
</style>
""", unsafe_allow_html=True)

# ── Session State ─────────────────────────────────────────────────────────────
if "messages"   not in st.session_state:
    st.session_state.messages   = []
if "memory"     not in st.session_state:
    st.session_state.memory     = []
if "history"    not in st.session_state:
    st.session_state.history    = []
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
if "graph"      not in st.session_state:
    with st.spinner("Loading ClaimSight agents..."):
        st.session_state.graph = build_graph()
if "last_result" not in st.session_state:
    st.session_state.last_result = None

# ── Hero Header ───────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <h1> ClaimSight Intelligence AI</h1>
    <p>Agentic intelligence that provides Insights of claims across two claims databases · 5 agents · MCP tools · 3-layer guardrails</p>
</div>
""", unsafe_allow_html=True)

# ── DB Stats Row ──────────────────────────────────────────────────────────────
db1_stats = get_db_stats("db1")
db2_stats = get_db_stats("db2")

c1, c2, c3, c4, c5 = st.columns(5)
with c1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value">{db1_stats.get('claims', 0)}</div>
        <div class="metric-label">DB1 Claims</div>
    </div>""", unsafe_allow_html=True)
with c2:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value">{db2_stats.get('claims', 0)}</div>
        <div class="metric-label">DB2 Claims</div>
    </div>""", unsafe_allow_html=True)
with c3:
    st.markdown(f"""
<div class="metric-card">
    <div class="metric-value" style="color:#ca4a4a">80</div>
    <div class="metric-label">Known Discrepancies</div>
</div>""", unsafe_allow_html=True)
with c4:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value" style="color:#4aca7e">{db1_stats.get('customers', 0)}</div>
        <div class="metric-label">Customers</div>
    </div>""", unsafe_allow_html=True)
with c5:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value" style="color:#4a9eca">{db1_stats.get('policies', 0)}</div>
        <div class="metric-label">Policies</div>
    </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Tabs ──────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs([
    "💬 Chat", "📊 Dashboard", "🔄 Diff View", "📋 Query History"
])

# ═══════════════════════════════════════════════════════════
# TAB 1 — CHAT
# ═══════════════════════════════════════════════════════════
with tab1:
    col_chat, col_side = st.columns([3, 1])

    with col_chat:
        # render past messages
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"], avatar="🟠" if msg["role"] == "user" else "🟢"):
                if msg["role"] == "assistant":
                    # agent path pills
                    pills = ""
                    for agent in msg.get("agent_path", []):
                        cls = {
                            "schema_agent":   "pill-schema",
                            "query_agent":    "pill-query",
                            "executor_agent": "pill-executor",
                            "analyst_agent":  "pill-analyst",
                            "chat_agent":     "pill-chat",
                            "input_rail":     "pill-blocked",
                        }.get(agent, "pill-chat")
                        label = agent.replace("_agent", "").replace("_", " ")
                        pills += f'<span class="agent-pill {cls}">{label}</span>'
                    st.markdown(pills, unsafe_allow_html=True)

                    # sql box
                    if msg.get("sql_query"):
                        st.markdown(
                            f'<div class="sql-box">⚡ {msg["sql_query"]}</div>',
                            unsafe_allow_html=True
                        )

                    st.markdown(msg["content"])

                    # stats row
                    if msg.get("db1_rows") is not None:
                        s1, s2, s3 = st.columns(3)
                        s1.metric("DB1 rows", msg["db1_rows"])
                        s2.metric("DB2 rows", msg["db2_rows"])
                        s3.metric("Anomalies", msg["anomalies"])
                else:
                    st.markdown(msg["content"])

        # chat input
        if prompt := st.chat_input("Ask anything about the claims data..."):
            with st.chat_message("user", avatar="🟠"):
                st.markdown(prompt)

            st.session_state.messages.append({
                "role": "user", "content": prompt
            })

            with st.chat_message("assistant", avatar="🤖"):
                with st.spinner("Running agents..."):
                    result = run_turn(
                        user_query = prompt,
                        memory     = st.session_state.memory,
                        session_id = st.session_state.session_id,
                        graph      = st.session_state.graph,
                    )

                st.session_state.last_result = result

                agent_path = result.get("agent_path", [])
                pills = ""
                for agent in agent_path:
                    cls = {
                        "schema_agent":   "pill-schema",
                        "query_agent":    "pill-query",
                        "executor_agent": "pill-executor",
                        "analyst_agent":  "pill-analyst",
                        "chat_agent":     "pill-chat",
                        "input_rail":     "pill-blocked",
                    }.get(agent, "pill-chat")
                    label = {
                                "schema_agent":   "schema",
                                "query_agent":    "query",
                                "executor_agent": "executor",
                                "analyst_agent":  "analyst",
                                "chat_agent":     "chat",
                                "input_rail":     "blocked",
                            }.get(agent, agent)
                    pills += f'<span class="agent-pill {cls}">{label}</span>'
                st.markdown(pills, unsafe_allow_html=True)

                sql = result.get("sql_query", "")
                if sql:
                    st.markdown(
                        f'<div class="sql-box">⚡ {sql}</div>',
                        unsafe_allow_html=True
                    )

                response = result.get("response", "Something went wrong.")
                st.markdown(response)

                db1_rows  = len(result.get("db1_results", []))
                db2_rows  = len(result.get("db2_results", []))
                anomalies = len(result.get("anomalies",   []))

                if db1_rows or db2_rows:
                    s1, s2, s3 = st.columns(3)
                    s1.metric("DB1 rows", db1_rows)
                    s2.metric("DB2 rows", db2_rows)
                    s3.metric("Anomalies", anomalies)

            st.session_state.messages.append({
                "role":       "assistant",
                "content":    response,
                "sql_query":  sql,
                "agent_path": agent_path,
                "db1_rows":   db1_rows,
                "db2_rows":   db2_rows,
                "anomalies":  anomalies,
            })

            st.session_state.memory.append(
                {"role": "user",      "content": prompt}
            )
            st.session_state.memory.append(
                {"role": "assistant", "content": response}
            )

            st.session_state.history.append({
                "query":      prompt,
                "sql":        sql,
                "db1_rows":   db1_rows,
                "db2_rows":   db2_rows,
                "anomalies":  anomalies,
                "agent_path": " → ".join(agent_path),
            })

            st.rerun()

    with col_side:
        st.markdown("#### 🤖 Agents")
        st.markdown("""
<div style="font-size:12px;color:#555;line-height:2">
<span class="agent-pill pill-schema">schema</span> discovers DB structure<br>
<span class="agent-pill pill-query">query</span> builds SQL<br>
<span class="agent-pill pill-executor">executor</span> runs on both DBs<br>
<span class="agent-pill pill-analyst">analyst</span> compares + reports<br>
<span class="agent-pill pill-chat">chat</span> answers you<br>
</div>
""", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("#### 💬 Try these")
        st.markdown("""
<div style="font-size:12px;color:#555;line-height:2.2">
→ Show all pending claims<br>
→ Compare both databases<br>
→ How many approved claims?<br>
→ Find discrepancies<br>
→ Show settled claims above 2 lakhs<br>
→ Which region has most claims?<br>
</div>
""", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🗑 Clear chat"):
            st.session_state.messages   = []
            st.session_state.memory     = []
            st.session_state.session_id = str(uuid.uuid4())
            st.rerun()

        st.markdown(
            f'<p style="font-size:11px;color:#333;margin-top:12px">'
            f'{len(st.session_state.messages)} messages</p>',
            unsafe_allow_html=True
        )

# ═══════════════════════════════════════════════════════════
# TAB 2 — DASHBOARD
# ═══════════════════════════════════════════════════════════
with tab2:
    st.markdown("#### 📊 Claims Overview")

    try:
        # status distribution
        status_db1 = execute_query(
            "SELECT status, COUNT(*) as count FROM claims GROUP BY status", "db1"
        )
        status_db2 = execute_query(
            "SELECT status, COUNT(*) as count FROM claims GROUP BY status", "db2"
        )

        col_d1, col_d2 = st.columns(2)

        with col_d1:
            st.markdown("**DB1 — Claims Primary**")
            if status_db1:
                df1 = pd.DataFrame(status_db1)
                st.bar_chart(df1.set_index("status"))

        with col_d2:
            st.markdown("**DB2 — Claims Replica**")
            if status_db2:
                df2 = pd.DataFrame(status_db2)
                st.bar_chart(df2.set_index("status"))

        st.divider()

        # claim type distribution
        st.markdown("#### Claims by Type")
        type_data = execute_query(
            "SELECT claim_type, COUNT(*) as count, "
            "ROUND(AVG(claim_amount), 2) as avg_amount "
            "FROM claims GROUP BY claim_type ORDER BY count DESC",
            "db1"
        )
        if type_data:
            df_type = pd.DataFrame(type_data)
            col_t1, col_t2 = st.columns(2)
            with col_t1:
                st.bar_chart(df_type.set_index("claim_type")["count"])
            with col_t2:
                st.dataframe(df_type, use_container_width=True)

        st.divider()

        # regional distribution
        st.markdown("#### Claims by Region")
        region_data = execute_query(
            "SELECT c.region, COUNT(cl.claim_id) as claims "
            "FROM customers c JOIN claims cl "
            "ON c.customer_id = cl.customer_id "
            "GROUP BY c.region ORDER BY claims DESC",
            "db1"
        )
        if region_data:
            df_region = pd.DataFrame(region_data)
            st.bar_chart(df_region.set_index("region"))

    except Exception as e:
        st.error(f"Dashboard error: {e}")

# ═══════════════════════════════════════════════════════════
# TAB 3 — DIFF VIEW
# ═══════════════════════════════════════════════════════════
with tab3:
    st.markdown("#### 🔄 Database Comparison — Live Diff")

    if st.button("🔍 Run Full Comparison", type="primary"):
        with st.spinner("Comparing both databases..."):
            from mcp_server.server import diff_results
            diff = diff_results(
                "SELECT claim_id, status, claim_amount FROM claims",
                key_col="claim_id"
            )

        summary = diff.get("summary", {})

        # summary metrics
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("DB1 Total",    summary.get("db1_total", 0))
        m2.metric("DB2 Total",    summary.get("db2_total", 0))
        m3.metric("Total Issues", summary.get("total_issues", 0),
                  delta=f"-{summary.get('total_issues', 0)}", delta_color="inverse")
        m4.metric("Mismatches",   summary.get("mismatch_count", 0))

        st.divider()

        col_g, col_o, col_m = st.columns(3)

        with col_g:
            st.markdown(f"**🔴 Ghost Rows — {summary.get('ghost_count', 0)}**")
            st.caption("In DB1, missing from DB2")
            for row in diff.get("ghost_rows", [])[:15]:
                data = row.get("db1_data", {})
                st.markdown(
                    f'<div class="diff-ghost">'
                    f'<b>{row["key"]}</b><br>'
                    f'Status: {data.get("status","—")} | '
                    f'₹{data.get("claim_amount","—"):,.0f}'
                    f'</div>',
                    unsafe_allow_html=True
                )

        with col_o:
            st.markdown(f"**🟢 Orphan Rows — {summary.get('orphan_count', 0)}**")
            st.caption("In DB2, missing from DB1")
            for row in diff.get("orphan_rows", [])[:15]:
                data = row.get("db2_data", {})
                st.markdown(
                    f'<div class="diff-orphan">'
                    f'<b>{row["key"]}</b><br>'
                    f'Status: {data.get("status","—")} | '
                    f'₹{data.get("claim_amount","—"):,.0f}'
                    f'</div>',
                    unsafe_allow_html=True
                )

        with col_m:
            st.markdown(f"**🟡 Mismatches — {summary.get('mismatch_count', 0)}**")
            st.caption("Same ID, different values")
            for row in diff.get("mismatches", [])[:15]:
                diffs = row.get("diffs", {})
                diff_text = " | ".join(
                    f'{k}: {v["db1"]} → {v["db2"]}'
                    for k, v in diffs.items()
                )
                st.markdown(
                    f'<div class="diff-mismatch">'
                    f'<b>{row["key"]}</b><br>'
                    f'{diff_text}'
                    f'</div>',
                    unsafe_allow_html=True
                )
    else:
        st.info("Click 'Run Full Comparison' to see live discrepancies between both databases.")

# ═══════════════════════════════════════════════════════════
# TAB 4 — QUERY HISTORY
# ═══════════════════════════════════════════════════════════
with tab4:
    st.markdown("#### Query History — This Session")

    if st.session_state.history:
        df_history = pd.DataFrame(st.session_state.history)
        st.dataframe(df_history, use_container_width=True)

        st.divider()
        st.markdown("#### SQL Queries Run")
        for i, item in enumerate(st.session_state.history, 1):
            if item.get("sql"):
                st.markdown(
                    f'<div class="sql-box">{i}. {item["sql"]}</div>',
                    unsafe_allow_html=True
                )
    else:
        st.info("No queries yet. Ask something in the Chat tab.")

# Sidebar 
with st.sidebar:
    st.markdown("### ClaimSight Intelligence Insights AI")
    st.markdown(
        '<p style="font-size:11px;color:#444">5-agent AI · MCP tools · 3-layer guardrails</p>',
        unsafe_allow_html=True
    )
    st.divider()

    st.markdown("### 🗄 Database Status")
    st.markdown(
        f'<p style="font-size:12px;color:#555">'
        f'DB1 claims: <b style="color:#7c6bff">{db1_stats.get("claims",0)}</b><br>'
        f'DB2 claims: <b style="color:#7c6bff">{db2_stats.get("claims",0)}</b><br>'
        f'Customers: <b style="color:#4aca7e">{db1_stats.get("customers",0)}</b><br>'
        f'Policies: <b style="color:#4a9eca">{db1_stats.get("policies",0)}</b>'
        f'</p>',
        unsafe_allow_html=True
    )
    st.divider()

    st.markdown("### 🛡 Guardrails")
    st.markdown(
        '<p style="font-size:12px;color:#555">'
        ' Input rail — injection blocked<br>'
        ' Query rail — read-only enforced<br>'
        ' Output rail — PII masked'
        '</p>',
        unsafe_allow_html=True
    )
    st.divider()

    st.markdown(
        f'<p style="font-size:11px;color:#333">'
        f'Session: {st.session_state.session_id[:8]}...</p>',
        unsafe_allow_html=True
    )
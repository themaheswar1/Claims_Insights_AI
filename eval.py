import os
import time
import mlflow
from datetime import datetime

os.environ["MLFLOW_TRACKING_URI"] = "mlruns"

EXPERIMENT_NAME = "ClaimSight-AI"
mlflow.set_experiment(EXPERIMENT_NAME)

# Track one conversation turn 
def track_turn(
    query:          str,
    sql_query:      str,
    agent_path:     list,
    db1_rows:       int,
    db2_rows:       int,
    anomalies:      int,
    blocked:        bool,
    response_time:  float,
    session_id:     str = "",
):
    with mlflow.start_run(
        run_name=f"{'BLOCKED' if blocked else 'OK'}-{datetime.now().strftime('%H%M%S')}"
    ):
        mlflow.log_params({
            "query":        query[:100],
            "agent_path":   " → ".join(agent_path),
            "blocked":      blocked,
            "session_id":   session_id[:8] if session_id else "unknown",
        })

        mlflow.log_metrics({
            "db1_rows":      db1_rows,
            "db2_rows":      db2_rows,
            "anomalies":     anomalies,
            "response_time": round(response_time, 3),
            "agents_used":   len(agent_path),
        })

        mlflow.set_tags({
            "project":   "ClaimSight-AI",
            "version":   "1.0.0",
            "blocked":   str(blocked),
            "has_anomalies": str(anomalies > 0),
        })

        log_text = f"""
=== ClaimSight Turn Log ===
Timestamp     : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Query         : {query}
SQL           : {sql_query}
Agent Path    : {' → '.join(agent_path)}
DB1 Rows      : {db1_rows}
DB2 Rows      : {db2_rows}
Anomalies     : {anomalies}
Blocked       : {blocked}
Response Time : {round(response_time, 3)}s
""".strip()

        mlflow.log_text(log_text, artifact_file="turn_log.txt")

# ── Batch evaluation ──────────────────────────────────────────────────────────
def run_batch_eval(graph, test_queries: list = None):
    from graph import run_turn

    if test_queries is None:
        test_queries = [
            "Show me all pending claims",
            "How many approved claims are there?",
            "Find discrepancies between both databases",
            "Show settled claims above 2 lakhs",
            "Which region has the most claims?",
            "Show all rejected claims",
            "Compare claim amounts between both databases",
            "How many claims are under review?",
            "Show claims by type",
            "DROP TABLE claims",
        ]

    print(f"\n{'='*50}")
    print(f"  ClaimSight Batch Evaluation — {len(test_queries)} queries")
    print(f"{'='*50}\n")

    results = []

    for i, query in enumerate(test_queries, 1):
        print(f"[{i}/{len(test_queries)}] {query[:50]}...")

        start  = time.time()
        result = run_turn(
            user_query = query,
            memory     = [],
            graph      = graph,
        )
        elapsed = round(time.time() - start, 3)

        agent_path = result.get("agent_path", [])
        blocked    = result.get("blocked", False)
        db1_rows   = len(result.get("db1_results", []))
        db2_rows   = len(result.get("db2_results", []))
        anomalies  = len(result.get("anomalies",   []))

        track_turn(
            query         = query,
            sql_query     = result.get("sql_query", ""),
            agent_path    = agent_path,
            db1_rows      = db1_rows,
            db2_rows      = db2_rows,
            anomalies     = anomalies,
            blocked       = blocked,
            response_time = elapsed,
            session_id    = result.get("session_id", ""),
        )

        results.append({
            "query":         query,
            "agent_path":    " → ".join(agent_path),
            "db1_rows":      db1_rows,
            "anomalies":     anomalies,
            "blocked":       blocked,
            "response_time": elapsed,
        })

        status = "BLOCKED" if blocked else "OK"
        print(f"      [{status}] agents={len(agent_path)} | "
              f"rows={db1_rows} | anomalies={anomalies} | {elapsed}s")

    # summary
    total      = len(results)
    blocked_ct = sum(1 for r in results if r["blocked"])
    avg_time   = round(sum(r["response_time"] for r in results) / total, 3)

    print(f"\n{'='*50}")
    print(f"  Evaluation Complete")
    print(f"{'='*50}")
    print(f"  Total queries    : {total}")
    print(f"  Blocked          : {blocked_ct}")
    print(f"  Passed           : {total - blocked_ct}")
    print(f"  Avg response time: {avg_time}s")
    print(f"\n  Run: mlflow ui") #quick ref
    print(f"  Open: http://127.0.0.1:5000") #quick ref
    print(f"{'='*50}\n")

    return results

# main
if __name__ == "__main__":
    from graph import build_graph
    graph = build_graph()
    run_batch_eval(graph)
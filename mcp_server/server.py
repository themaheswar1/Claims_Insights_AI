import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mcp.server.fastmcp import FastMCP
from core.database import get_schema, execute_query, get_db_stats

mcp = FastMCP("claimsight-tools")

# tool-1 List tables

@mcp.tool()
def list_tables(db: str = "db1") -> dict:
    return get_schema(db)

# tool-2 Inspect Schema
@mcp.tool()
def inspect_schema(db: str = "db1") -> str:
    schema = get_schema(db)
    lines = [f"Schema for {db.upper()}:"]

    for table, info in schema.items():
        lines.append(f"\n Table: {table}")
        for col,typ in zip(info["columns"], info["types"]):
            lines.append(f" - {col} ({typ})")
    return "\n".join(lines)

# tool-3 Validate SQL
@mcp.tool()
def validate_sql(query: str) -> dict:
    forbidden = [
        "DROP", "DELETE", "INSERT",
        "UPDATE", "TRUNCATE", "ALTER",
        "CREATE", "REPLACE", "ATTACH"
    ]

    query_upper = query.strip().upper()

    # must start with SELECT
    if not query_upper.startswith("SELECT"):
        return {
            "valid":  False,
            "reason": "Only SELECT queries are allowed."
        }

    # check for forbidden keywords
    for word in forbidden:
        if word in query_upper:
            return {
                "valid":  False,
                "reason": f"Forbidden keyword detected: {word}"
            }

    # check for SQL injection patterns
    injection_patterns = ["--", "/*", "*/", "xp_", "EXEC(", "EXECUTE("]
    for pattern in injection_patterns:
        if pattern.upper() in query_upper:
            return {
                "valid":  False,
                "reason": f"Potential SQL injection pattern detected: {pattern}"
            }

    return {"valid": True, "reason": "Query is safe to execute."}

#tool-4 Execute query
@mcp.tool()
def run_query(query: str, db: str = "db1") -> dict:
    #validating before executing
    validation = validate_sql(query)
    if not validation["valid"]:
        return{
            "rows": [],
            "row_count":0,
            "error": validation["reason"]
        }
    
    try:
        rows = execute_query(query,db)
        return{
            "rows":      rows,
            "row_count": len(rows),
            "error":     None
        }
    except Exception as e:
        return{
            "rows":      [],
            "row_count": 0,
            "error":     str(e)
        }
    
# tool-5 Diff Results
@mcp.tool()
def diff_results(query: str, key_col: str = "claim_id") -> dict:
    db1_data = run_query(query, "db1")    
    db2_data = run_query(query, "db2")

    if db1_data.get("error"):
        return {"error": f"DB1 error: {db1_data['error']}"}
    if db2_data.get("error"):
        return {"error": f"DB2 error: {db2_data['error']}"}

    db1_rows = {row[key_col]: row for row in db1_data["rows"] if key_col in row}
    db2_rows = {row[key_col]: row for row in db2_data["rows"] if key_col in row}

    db1_keys = set(db1_rows.keys())
    db2_keys = set(db2_rows.keys())

    # ghost rows — exist in DB1 but not DB2
    ghost_rows = [
        {"key": k, "db1_data": db1_rows[k]}
        for k in db1_keys - db2_keys
    ]

    # orphan rows — exist in DB2 but not DB1
    orphan_rows = [
        {"key": k, "db2_data": db2_rows[k]}
        for k in db2_keys - db1_keys
    ]

    # mismatches — exist in both but values differ
    mismatches = []
    for key in db1_keys & db2_keys:
        db1_row = db1_rows[key]
        db2_row = db2_rows[key]
        diff_fields = {}

        for col in db1_row:
            if col in db2_row and db1_row[col] != db2_row[col]:
                diff_fields[col] = {
                    "db1": db1_row[col],
                    "db2": db2_row[col]
                }

        if diff_fields:
            mismatches.append({
                "key":    key,
                "diffs":  diff_fields
            })

    return {
        "ghost_rows":  ghost_rows,
        "orphan_rows": orphan_rows,
        "mismatches":  mismatches,
        "summary": {
            "db1_total":     len(db1_rows),
            "db2_total":     len(db2_rows),
            "ghost_count":   len(ghost_rows),
            "orphan_count":  len(orphan_rows),
            "mismatch_count": len(mismatches),
            "total_issues":  len(ghost_rows) + len(orphan_rows) + len(mismatches)
        }
    } 

# tool-6 DB Stats
@mcp.tool()
def database_stats() -> dict:
    return {
        "db1": get_db_stats("db1"),
        "db2": get_db_stats("db2"),
    }   

# tool-7 Explain Query  
@mcp.tool()
def explain_query(query: str) -> dict:
    
    validation = validate_sql(query)
    if not validation["valid"]:
        return {"error": validation["reason"]}

    try:
        explanation = execute_query(f"EXPLAIN QUERY PLAN {query}", "db1")
        return {"steps": explanation}
    except Exception as e:
        return {"error": str(e)}
    
# Main    
if __name__ == "__main__":
    print("=" * 45)
    print("  ClaimSight — MCP Server Test")
    print("=" * 45)

    print("\n[1/4] Testing list_tables...")
    result = list_tables("db1")
    for table in result:
        print(f"  ✅ {table}: {result[table]['columns']}")

    print("\n[2/4] Testing validate_sql...")
    good = validate_sql("SELECT * FROM claims WHERE status = 'PENDING'")
    bad  = validate_sql("DROP TABLE claims")
    print(f"  ✅ Good query: {good}")
    print(f"  ✅ Bad query:  {bad}")

    print("\n[3/4] Testing run_query...")
    rows = run_query("SELECT claim_id, status, claim_amount FROM claims LIMIT 3", "db1")
    print(f"  ✅ Rows returned: {rows['row_count']}")
    for row in rows["rows"]:
        print(f"     {row}")

    print("\n[4/4] Testing diff_results...")
    diff = diff_results("SELECT claim_id, status, claim_amount FROM claims")
    print(f"  ✅ Ghost rows:   {diff['summary']['ghost_count']}")
    print(f"  ✅ Orphan rows:  {diff['summary']['orphan_count']}")
    print(f"  ✅ Mismatches:   {diff['summary']['mismatch_count']}")
    print(f"  ✅ Total issues: {diff['summary']['total_issues']}")

    print("\n✅ MCP Server tools working.")
    print("=" * 45)
import re

ALLOWED_STATEMENTS = ["SELECT"]

FORBIDDEN_KEYWORDS = [
    "DROP", "DELETE", "INSERT", "UPDATE",
    "TRUNCATE", "ALTER", "CREATE", "REPLACE",
    "ATTACH", "DETACH", "PRAGMA", "VACUUM",
]

def check_query(sql_query: str) -> dict:
    """
    Enforces read-only SQL before execution.
    Called after Agent 2 builds the query,
    before Agent 3 runs it.
    Returns:
        dict with allowed (bool) and reason (str)
    """
    if not sql_query or not sql_query.strip():
        return {"allowed": False, "reason": "Empty SQL query."}

    query_upper = sql_query.strip().upper()

    # must start with SELECT
    first_word = query_upper.split()[0]
    if first_word not in ALLOWED_STATEMENTS:
        return {
            "allowed": False,
            "reason":  f"Only SELECT statements allowed. Got: {first_word}"
        }

    # check for forbidden keywords anywhere in query
    for keyword in FORBIDDEN_KEYWORDS:
        if re.search(rf"\b{keyword}\b", query_upper):
            return {
                "allowed": False,
                "reason":  f"Forbidden keyword in SQL: {keyword}"
            }

    # check for multiple statements (semicolon attack)
    statements = [s.strip() for s in sql_query.split(";") if s.strip()]
    if len(statements) > 1:
        return {
            "allowed": False,
            "reason":  "Multiple SQL statements detected. Only one statement allowed."
        }

    return {"allowed": True, "reason": "Query passed read-only check."}
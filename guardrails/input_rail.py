import re

# ── Blocked patterns ──────────────────────────────────────────────────────────
INJECTION_KEYWORDS = [
    "drop", "delete", "insert", "update", "truncate",
    "alter", "create", "replace", "attach", "detach",
    "pragma", "vacuum", "reindex",
]

INJECTION_PATTERNS = [
    r"(--)|(\/\*)|(\*\/)",           # SQL comments
    r"(;)\s*(select|drop|delete)",   # chained statements
    r"(xp_|exec\s*\(|execute\s*\()", # stored procedures
    r"(union\s+select)",             # union injection
    r"(1\s*=\s*1|1\s*=\s*'1')",     # always-true conditions
]

PROMPT_INJECTION_PATTERNS = [
    "ignore previous instructions",
    "ignore all instructions",
    "forget your instructions",
    "you are now",
    "act as",
    "jailbreak",
    "disregard",
]

# ── Main rail function ────────────────────────────────────────────────────────
def check_input(user_query: str) -> dict:
    """
    Scans user query before any agent processes it.
    Returns:
        dict with allowed (bool) and reason (str)
    """
    query_lower = user_query.lower().strip()

    # empty input
    if not query_lower:
        return {"allowed": False, "reason": "Empty query received."}

    # too long — potential prompt stuffing
    if len(user_query) > 2000:
        return {"allowed": False, "reason": "Query too long. Maximum 2000 characters."}

    # SQL injection keywords in natural language
    for keyword in INJECTION_KEYWORDS:
        if re.search(rf"\b{keyword}\b", query_lower):
            return {
                "allowed": False,
                "reason":  f"Query contains restricted keyword: '{keyword}'. "
                           f"Only data retrieval requests are allowed."
            }

    # SQL injection patterns
    for pattern in INJECTION_PATTERNS:
        if re.search(pattern, query_lower, re.IGNORECASE):
            return {
                "allowed": False,
                "reason":  "Query contains a suspicious pattern and was blocked."
            }

    # prompt injection attempts
    for phrase in PROMPT_INJECTION_PATTERNS:
        if phrase in query_lower:
            return {
                "allowed": False,
                "reason":  "Query contains an instruction override attempt and was blocked."
            }

    return {"allowed": True, "reason": "Input is clean."}
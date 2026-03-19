import re

# ── PII patterns to mask ──────────────────────────────────────────────────────
PII_PATTERNS = [
    # Email addresses
    (r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", "[EMAIL REDACTED]"),

    # Indian phone numbers
    (r"(\+91[\-\s]?)?[6-9]\d{9}", "[PHONE REDACTED]"),

    # Phone with dashes/spaces
    (r"\b\d{3}[-.\s]\d{3}[-.\s]\d{4}\b", "[PHONE REDACTED]"),

    # Aadhaar-style numbers (12 digits)
    (r"\b\d{4}[\s-]\d{4}[\s-]\d{4}\b", "[ID REDACTED]"),

    # PAN card style
    (r"\b[A-Z]{5}[0-9]{4}[A-Z]{1}\b", "[PAN REDACTED]"),
]

# ── Sensitive field names to mask in data rows ────────────────────────────────
SENSITIVE_FIELDS = ["phone", "email", "full_name"]

def mask_pii_in_text(text: str) -> str:
    """
    Scans response text and masks PII patterns.
    Args:
        text: raw response string from any agent
    Returns:
        text with PII replaced by redaction labels
    """
    for pattern, replacement in PII_PATTERNS:
        text = re.sub(pattern, replacement, text)
    return text

def mask_pii_in_rows(rows: list[dict]) -> list[dict]:
    """
    Masks sensitive fields in database result rows
    before they reach the UI.
    Args:
        rows: list of dicts from execute_query()
    Returns:
        rows with sensitive fields masked
    """
    masked = []
    for row in rows:
        clean_row = {}
        for key, value in row.items():
            if key.lower() in SENSITIVE_FIELDS:
                clean_row[key] = "[REDACTED]"
            else:
                clean_row[key] = value
        masked.append(clean_row)
    return masked

def check_output(response: str, rows: list[dict] = None) -> dict:
    """
    Final gate before any response reaches the user.
    Masks PII in both text and data rows.
    Args:
        response: agent response text
        rows:     optional list of data rows to mask
    Returns:
        dict with clean_response (str) and clean_rows (list)
    """
    clean_response = mask_pii_in_text(response)
    clean_rows     = mask_pii_in_rows(rows) if rows else []

    return {
        "clean_response": clean_response,
        "clean_rows":     clean_rows,
    }
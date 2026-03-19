import sqlite3
import os
from contextlib import contextmanager
from dotenv import load_dotenv

load_dotenv()

# Path config

DB1_PATH = os.getenv("DB1_PATH","data/db1_claims_primary.sqlite")
DB2_PATH = os.getenv("DB2_PATH", "data/db2_claims_replica.sqlite")

# Connection Manager


@contextmanager
def get_connection(db: str = "db1"):

    path = DB1_PATH if db == "db1" else DB2_PATH

    if not os.path.exists(path):
        raise FileNotFoundError(
            f"Database not found: {path}\n"
            f"Run generate_data.py first."
        )

    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row   # rows behave like dicts
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA journal_mode = WAL")

    try:
        yield conn
    finally:
        conn.close()


# Schema validation

def get_schema(db: str = "db1") -> dict:
    
    schema = {}

    with get_connection(db) as conn:
        tables = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).fetchall()

        for table in tables:
            table_name = table["name"]
            columns    = conn.execute(
                f"PRAGMA table_info({table_name})"
            ).fetchall()

            schema[table_name] = {
                "columns": [col["name"] for col in columns],
                "types":   [col["type"] for col in columns],
            }

    return schema

# only safe queries to accept

def execute_query(query: str, db: str = "db1") -> list[dict]:

    forbidden = ["DROP","TRUNCATE","INSERT","UPDATE","DELETE","ALTER","CREATE"]

    query_upper = query.strip().upper()
    for word in forbidden:
        if word in query_upper:
            raise ValueError(
                f"Query contains forbidden keyword: {word}."
                f"Only SELECT queries are allowed."
            )
    with get_connection(db) as conn:
        rows = conn.execute(query).fetchall()
        return [dict(row) for row in rows]

# Stats of our db's
def get_db_stats(db: str = "db1") -> dict:
    
    stats = {"db": db}

    with get_connection(db) as conn:
        tables = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).fetchall()

        for table in tables:
            name  = table["name"]
            count = conn.execute(
                f"SELECT COUNT(*) as cnt FROM {name}"
            ).fetchone()["cnt"]
            stats[name] = count

    return stats   

# Testing connection

if __name__ == "__main__":
    print("=" * 45)
    print("  ClaimSight — Database Connection Test")
    print("=" * 45)

    for db in ["db1", "db2"]:
        print(f"\n[{db.upper()}] Stats:")
        stats = get_db_stats(db)
        for table, count in stats.items():
            if table != "db":
                print(f"  {table:15} → {count} rows")

    print(f"\n[Schema — DB1]:")
    schema = get_schema("db1")
    for table, info in schema.items():
        print(f"  {table}: {', '.join(info['columns'])}")

    print("\n✅ Both databases connected successfully.")
    print("=" * 45)    
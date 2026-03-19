import sqlite3
import random
import os
from datetime import datetime,timedelta
from faker import Faker

fake = Faker("en_IN")
random.seed(42)
Faker.seed(42)

# General configuration

DB1_PATH = "data/db1_claims_primary.sqlite"
DB2_PATH = "data/db2_claims_replica.sqlite"
NUM_ROWS = 1000
CLAIM_TYPES = ["Health","Motor","Life","Property","Travel"]
CLAIM_STATUSES = ["PENDING","APPROVED","REJECTED","SETTLED","UNDER_REVIEW"]
POLICY_TYPES = ["Individual","Family","Group","Term","ULIP"]
REGIONS        = ["North", "South", "East", "West", "Central"]

# helpers
def random_date(start_year=2022, end_year=2024):
    start = datetime(start_year, 1, 1)
    end = datetime(end_year, 12, 31)
    return (start + timedelta(days=random.randint(0, (end -start).days)))

def random_amount(low, high):
    return round(random.uniform(low, high), 2)

# Schema
def create_schema(conn):
    cur = conn.cursor()

    cur.execute("""

    CREATE TABLE IF NOT EXISTS customers (
                customer_id  TEXT PRIMARY KEY,
                full_name    TEXT NOT NULL,
                age          INTEGER,
                phone        TEXT,
                email        TEXT,
                region       TEXT,
                policy_type  TEXT,
                premium_amount REAL
                )
"""
    )

    cur.execute("""
        CREATE TABLE IF NOT EXISTS policies (
            policy_id        TEXT PRIMARY KEY,
            customer_id      TEXT,
            policy_type      TEXT,
            start_date       TEXT,
            end_date         TEXT,
            coverage_amount  REAL,
            FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
        )

""")
    cur.execute("""
        CREATE TABLE IF NOT EXISTS claims (
            claim_id           TEXT PRIMARY KEY,
            policy_id          TEXT,
            customer_id        TEXT,
            claim_date         TEXT,
            claim_type         TEXT,
            claim_amount       REAL,
            status             TEXT,
            settlement_amount  REAL,
            settlement_date    TEXT,
            remarks            TEXT,
            FOREIGN KEY (policy_id)   REFERENCES policies(policy_id),
            FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
        )
""")
    conn.commit()

# Generate Base Data
def generate_base_data():
    customers = []
    policies = []
    claims = []

    for i in range(1, NUM_ROWS+1):
        cid = f"CUST-{i:04d}"
        pid = f"POL-{i:04d}"
        clm = f"CLM-{i:04d}"

        # customer
        customers.append((
            cid,
            fake.name(),
            random.randint(22,70),
            fake.phone_number()[:15],
            fake.email(),
            random.choice(REGIONS),
            random.choice(POLICY_TYPES),
            random_amount(5000, 50000),
        ))   
        # policy
        start = random_date(2020,2022)
        end = random_date(2023, 2025)
        policies.append((
            pid,cid,random.choice(POLICY_TYPES),start,end,random_amount(100000,5000000),
        )) 
        #claim
        claim_amt = random_amount(10000, 500000)
        status = random.choice(CLAIM_STATUSES)
        settlement_amt = round(claim_amt*random.uniform(0.7,1.0),2) if status == "SETTLED" else None
        settlement_dt = random_date(2023,2024) if status == "SETTLED" else None

        claims.append((
            clm, pid, cid,
            random_date(2022,2024),
            random.choice(CLAIM_TYPES),
            claim_amt,
            status,
            settlement_amt,
            settlement_dt,
            fake.sentence(nb_words=6),
        ))

    return customers, policies, claims

# Insert Data
def insert_data(conn, customers, policies, claims):
    cur = conn.cursor()
    cur.executemany("INSERT INTO customers VALUES (?,?,?,?,?,?,?,?)", customers) 
    cur.executemany("INSERT INTO policies  VALUES (?,?,?,?,?,?)",     policies)
    cur.executemany("INSERT INTO claims    VALUES (?,?,?,?,?,?,?,?,?,?)", claims)
    conn.commit()

# Engineer anamolies into DB2

def engineer_discrepancies(conn2):
    cur = conn2.cursor()
    print("\n  Engineering discrepancies into DB2...")

    # Type 1 — Ghost rows: 20 claims exist in DB1 but deleted from DB2
    ghost_ids = [f"CLM-{i:04d}" for i in random.sample(range(1, 201), 20)]
    cur.executemany("DELETE FROM claims WHERE claim_id = ?",
                    [(cid,) for cid in ghost_ids])
    print(f" Type 1 — Ghost rows     : {len(ghost_ids)} claims deleted from DB2")


    # Type 2 — Status drift: 20 claims have different status in DB2
    status_ids = [f"CLM-{i:04d}" for i in random.sample(range(201, 401), 20)]
    for cid in status_ids:
        cur.execute("SELECT status FROM claims WHERE claim_id = ?", (cid,))
        row = cur.fetchone()
        if row:
            old_status = row[0]
            new_status = random.choice([s for s in CLAIM_STATUSES if s != old_status])
            cur.execute("UPDATE claims SET status = ? WHERE claim_id = ?",
                        (new_status, cid))
    print(f" Type 2 — Status drift   : {len(status_ids)} claims updated in DB2")

    # Type 3 — Amount drift: 20 claims have different claim_amount in DB2
    amount_ids = [f"CLM-{i:04d}" for i in random.sample(range(401, 601), 20)]
    for cid in amount_ids:
        cur.execute("SELECT claim_amount FROM claims WHERE claim_id = ?", (cid,))
        row = cur.fetchone()
        if row:
            new_amount = round(row[0] * random.uniform(0.85, 1.15), 2)
            cur.execute("UPDATE claims SET claim_amount = ? WHERE claim_id = ?",
                        (new_amount, cid))
    print(f" Type 3 — Amount drift   : {len(amount_ids)} amounts changed in DB2")

    # Type 4 — Orphan rows: 20 claims exist only in DB2
    for i in range(1001, 1021):
        clm = f"CLM-{i:04d}"
        cid = f"CUST-{random.randint(1, 1000):04d}"
        pid = f"POL-{random.randint(1, 1000):04d}"
        claim_amt = random_amount(10000, 500000)
        status    = random.choice(CLAIM_STATUSES)
        conn2.execute("""
            INSERT INTO claims VALUES (?,?,?,?,?,?,?,?,?,?)
        """, (
            clm, pid, cid,
            random_date(2022, 2024),
            random.choice(CLAIM_TYPES),
            claim_amt, status,
            None, None,
            fake.sentence(nb_words=6),
        ))
    print(f" Type 4 — Orphan rows    : 20 claims added only to DB2")

    conn2.commit()
    print(f"\n  Total discrepancies engineered: 80")

# Main

if __name__ == "__main__":
    print("=" * 55)
    print("  Claim_Sight-AI — Data Generation Pipeline")
    print("=" * 55)

    os.makedirs("data", exist_ok=True)

    # remove existing DBs
    for path in [DB1_PATH, DB2_PATH]:
        if os.path.exists(path):
            os.remove(path)

    print("\n[1/4] Generating base data...")
    customers, policies, claims = generate_base_data()
    print(f"      ✓ {len(customers)} customers, {len(policies)} policies, {len(claims)} claims")

    print("\n[2/4] Building DB1 — Claims Primary...")
    conn1 = sqlite3.connect(DB1_PATH)
    create_schema(conn1)
    insert_data(conn1, customers, policies, claims)
    conn1.close()
    print(f"      ✓ DB1 ready → {DB1_PATH}")

    print("\n[3/4] Building DB2 — Claims Replica...")
    conn2 = sqlite3.connect(DB2_PATH)
    create_schema(conn2)
    insert_data(conn2, customers, policies, claims)

    print("\n[4/4] Engineering discrepancies into DB2...")
    engineer_discrepancies(conn2)
    conn2.close()
    print(f"      ✓ DB2 ready → {DB2_PATH}")

    print("\n" + "=" * 55)
    print("  Both databases ready. 80 discrepancies engineered.")
    print("  DB1 → 1000 claims (clean)")
    print("  DB2 → 1000 claims (with 80 deliberate differences)")
    print("=" * 55 + "\n") 

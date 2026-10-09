import json, subprocess, os, sqlite3
from datetime import datetime

DB_PATH = "C:/workspace/customer-hub/customers.db"

def run_boss(args):
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    r = subprocess.run(["boss-cli"] + args, capture_output=True, text=True, encoding="utf-8", env=env)
    return json.loads(r.stdout)

def sync():
    data = run_boss([
        "customer", "list",
        "--filter", '{"signStatus":"已成交"}',
        "--fields", "id,organizationUuid,organizationName,manualStarLevel,customerSuccess,technicalSupport,healthIndicator"
    ])
    orgs = data["data"]["organizations"]
    conn = sqlite3.connect(DB_PATH)
    count = 0
    for c in orgs:
        health = c.get("healthIndicator")
        if health is not None and health != "":
            try:
                health = float(health)
            except:
                health = None
        conn.execute("""
            INSERT INTO customers (boss_id, org_uuid, org_name, manual_star_level, customer_success, technical_support, health_indicator, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(boss_id) DO UPDATE SET
                org_uuid=excluded.org_uuid, org_name=excluded.org_name,
                manual_star_level=excluded.manual_star_level, customer_success=excluded.customer_success,
                technical_support=excluded.technical_support, health_indicator=excluded.health_indicator,
                updated_at=excluded.updated_at
        """, (
            c["id"],
            c.get("organizationUuid"),
            c["organizationName"],
            c.get("manualStarLevel"),
            c.get("customerSuccess"),
            c.get("technicalSupport"),
            health,
            datetime.now()
        ))
        count += 1
    conn.execute("INSERT INTO sync_log (count) VALUES (?)", (count,))
    conn.commit()
    conn.close()
    print(f"OK: {count} customers synced at {datetime.now()}")

if __name__ == "__main__":
    sync()
import sqlite3, json, datetime

DB = "C:/workspace/customer-hub/customers.db"
with open("C:/workspace/customer-hub/debug2.json", "r", encoding="utf-8") as f:
    results = json.load(f)

conn = sqlite3.connect(DB)
count = 0
for item in results["feishu"]:
    row = conn.execute("SELECT boss_id FROM customers WHERE org_name=?", (item["cust"],)).fetchone()
    if not row:
        print("NOT FOUND:", item["cust"])
        continue
    boss_id = row[0]
    conn.execute(
        "UPDATE customers SET im_type=?, im_group_id=?, updated_at=? WHERE boss_id=?",
        ("feishu", item["chat_id"], datetime.datetime.now().isoformat(), boss_id)
    )
    count += 1
conn.commit()

feishu_count = conn.execute("SELECT COUNT(*) FROM customers WHERE im_type='feishu'").fetchone()[0]
dingtalk_count = conn.execute("SELECT COUNT(*) FROM customers WHERE im_type='dingtalk'").fetchone()[0]
unset_count = conn.execute("SELECT COUNT(*) FROM customers WHERE im_type IS NULL").fetchone()[0]
conn.close()
print(f"Written {count} feishu matches")
print(f"Total: feishu={feishu_count}, dingtalk={dingtalk_count}, unset={unset_count}")
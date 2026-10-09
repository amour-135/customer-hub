import json, sqlite3, re
from datetime import datetime

DB = "C:/workspace/customer-hub/customers.db"

# ── 1. 拉飞书群列表 ──────────────────────────────────────────────
import subprocess, os
env = os.environ.copy()
env["PYTHONIOENCODING"] = "utf-8"
feishu_result = subprocess.run(
    ["C:/Users/Lenovo/AppData/Local/Microsoft/WinGet/Packages/ByteDance.LarkCLI_Microsoft.Winget.Source_8wekyb3d8bbwe/lark-cli.exe",
     "im", "+chat-list", "--page-all"],
    capture_output=True, text=True, encoding="utf-8", env=env
)
feishu_data = json.loads(feishu_result.stdout)
feishu_chats = feishu_data["data"]["chats"]

# ── 2. 拉钉钉群列表 ──────────────────────────────────────────────
dingtalk_result = subprocess.run(
    ["C:/Users/Lenovo/AppData/Local/Microsoft/WinGet/Packages/Alibaba.DingTalkWorkspaceCLI_Microsoft.Winget.Source_8wekyb3d8bbwe/dws.exe",
     "chat", "+chat-list", "--page-all", "--types", "group"],
    capture_output=True, text=True, encoding="utf-8", env=env
)
dingtalk_data = json.loads(dingtalk_result.stdout)
dingtalk_chats = dingtalk_data["chats"]

print(f"飞书群: {len(feishu_chats)} 个")
print(f"钉钉群: {len(dingtalk_chats)} 个")

# ── 3. 加载客户列表 ──────────────────────────────────────────────
conn = sqlite3.connect(DB)
conn.row_factory = sqlite3.Row
customers = conn.execute("SELECT boss_id, org_name FROM customers").fetchall()
conn.close()

# ── 4. 匹配函数 ─────────────────────────────────────────────────
# 去除常见后缀，提取可用于匹配的关键词
def extract_keywords(name):
    name = name.replace("影刀内部沟通群", "").replace("影刀售后服务群", "")
    name = name.replace("影刀项目沟通群", "").replace("影刀RPA", "").replace("&", " ")
    name = name.replace("|", " ").replace("-", " ").replace("—", " ")
    name = name.replace("&", " ").replace("×", " ").replace("✖", " ")
    return name.strip()

def name_match(chat_name, customer_name):
    cn = extract_keywords(chat_name).lower()
    # 客户名去公司后缀
    cust = customer_name.replace("有限公司", "").replace("股份有限公司", "")
    cust = cust.replace("集团有限公司", "").replace("有限责任公司", "")
    cust = cust.replace("（浙江）", "").replace("浙江", "")
    cust_keywords = [k for k in cust if len(k) >= 2]
    return any(k.lower() in cn for k in cust_keywords)

# ── 5. 逐个匹配 ─────────────────────────────────────────────────
conn = sqlite3.connect(DB)
matched = {"feishu": [], "dingtalk": [], "none": []}
updates = []

for cust in customers:
    found = False
    cust_name = cust["org_name"]

    # 飞书
    for chat in feishu_chats:
        if name_match(chat["name"], cust_name):
            updates.append(("feishu", chat["chat_id"], "", cust["boss_id"]))
            matched["feishu"].append(cust_name)
            found = True
            break

    # 钉钉
    if not found:
        for chat in dingtalk_chats:
            if name_match(chat["name"], cust_name):
                updates.append(("dingtalk", chat["openConversationId"], "", cust["boss_id"]))
                matched["dingtalk"].append(cust_name)
                found = True
                break

    if not found:
        matched["none"].append(cust_name)

# ── 6. 写入数据库 ─────────────────────────────────────────────────
for im_type, im_group_id, im_group_url, boss_id in updates:
    conn.execute(
        "UPDATE customers SET im_type=?, im_group_id=?, im_group_url=?, updated_at=? WHERE boss_id=?",
        (im_type, im_group_id, im_group_url, datetime.now().isoformat(), boss_id)
    )
conn.commit()
conn.close()

print(f"\n匹配结果:")
print(f"  飞书: {len(matched['feishu'])} 家")
for n in matched["feishu"]: print(f"    {n}")
print(f"  钉钉: {len(matched['dingtalk'])} 家")
for n in matched["dingtalk"]: print(f"    {n}")
print(f"  未匹配: {len(matched['none'])} 家")
for n in matched["none"]: print(f"    {n}")
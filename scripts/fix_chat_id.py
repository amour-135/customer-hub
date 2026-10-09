import json, sqlite3

DB = 'C:/workspace/customer-hub/customers.db'
conn = sqlite3.connect(DB)
conn.row_factory = sqlite3.Row
customers = conn.execute('SELECT boss_id, org_name FROM customers').fetchall()
conn.close()

import subprocess, os
env = os.environ.copy()
env['PYTHONIOENCODING'] = 'utf-8'
r = subprocess.run(
    ['C:/Users/Lenovo/AppData/Local/Microsoft/WinGet/Packages/ByteDance.LarkCLI_Microsoft.Winget.Source_8wekyb3d8bbwe/lark-cli.exe',
     'im', '+chat-list', '--page-all'],
    capture_output=True, text=True, encoding='utf-8', env=env
)
feishu_data = json.loads(r.stdout)
feishu_chats = {c['name']: c for c in feishu_data['data']['chats']}

def match_chat(chat_name, cust_name):
    chat_core = chat_name
    for suffix in ['影刀内部沟通群','影刀售后服务群','影刀项目沟通群','影刀RPA','-内部沟通群','&影刀内部沟通群','-影刀内部沟通群','&影刀售后服务群','&影刀项目沟通群']:
        chat_core = chat_core.replace(suffix,'').strip()
    for suffix in ['有限公司','股份有限公司','集团有限公司','有限责任公司','（浙江）','（杭州）','浙江','杭州']:
        chat_core = chat_core.replace(suffix,'')
    chat_core = chat_core.strip().lower()
    cust_short = cust_name.replace('有限公司','').replace('股份有限公司','').replace('集团有限公司','').replace('有限责任公司','').replace('（浙江）','').replace('（杭州）','').replace('浙江','').replace('杭州','').strip().lower()
    if len(cust_short) >= 4:
        return cust_short in chat_core
    return False

conn = sqlite3.connect(DB)
updated = 0
for cust in customers:
    for chat_name, chat in feishu_chats.items():
        if match_chat(chat_name, cust['org_name']):
            conn.execute(
                'UPDATE customers SET im_type=?,im_group_id=?,im_group_url=?,updated_at=? WHERE boss_id=?',
                ('feishu', chat['chat_id'], chat.get('chat_app_link',''), 'fixed', cust['boss_id'])
            updated += 1
            break
conn.commit()
print('Updated:', updated, 'records')
conn.close()
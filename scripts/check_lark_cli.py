import json, subprocess, os
env = os.environ.copy()
env['PYTHONIOENCODING'] = 'utf-8'
r = subprocess.run(
    ['C:/Users/Lenovo/AppData/Local/Microsoft/WinGet/Packages/ByteDance.LarkCLI_Microsoft.Winget.Source_8wekyb3d8bbwe/lark-cli.exe',
     'im', '+chat-list', '--page-all'],
    capture_output=True, text=True, encoding='utf-8', env=env
)
data = json.loads(r.stdout)
chats = data['data']['chats']
# Print first 3 chats with all ID fields
for c in chats[:3]:
    print('name:', c['name'])
    print('chat_id:', c['chat_id'])
    print('chat_app_link:', c.get('chat_app_link',''))
    print('---')
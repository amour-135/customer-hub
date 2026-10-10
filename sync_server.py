import http.server, socketserver, subprocess, json, threading, os, sys
from datetime import datetime

PORT = 3847
REPO_DIR = r'C:\Users\Lenovo\Documents\ChatGPT\客户建联中台'
CUSTOMERS_JSON = os.path.join(REPO_DIR, 'customers.json')
MAIN_JS = os.path.join(REPO_DIR, 'actix-web', 'src', 'main.js')
BOSS_CLI = r'C:\Users\Lenovo\.local\bin\boss-cli.exe'

syncing = False

def run_boss(args):
    env = os.environ.copy()
    env['PYTHONIOENCODING'] = 'utf-8'
    r = subprocess.run(args, capture_output=True, text=True, encoding='utf-8', env=env)
    return json.loads(r.stdout)

def do_sync():
    global syncing
    if syncing:
        return {'ok': False, 'msg': '同步中，请稍候'}
    syncing = True
    try:
        # 1. 同步BOSS
        data = run_boss([BOSS_CLI, 'customer', 'list',
            '--filter', '{"signStatus":"已成交"}',
            '--fields', 'id,organizationUuid,organizationName,manualStarLevel,customerSuccess,technicalSupport,healthIndicator'])
        orgs = data['data']['organizations']

        # 读取已有建联数据
        existing = {}
        if os.path.exists(CUSTOMERS_JSON):
            with open(CUSTOMERS_JSON, 'r', encoding='utf-8') as f:
                for c in json.load(f):
                    key = c.get('boss_id') or c.get('org_uuid')
                    if key:
                        existing[key] = c

        customers = []
        for c in orgs:
            boss_id = c.get('id')
            key = boss_id or c.get('organizationUuid')
            existing_c = existing.get(key, {})
            health = c.get('healthIndicator')
            if health is not None and health != '':
                try: health = float(health)
                except: health = None
            customers.append({
                'boss_id': boss_id,
                'org_name': c.get('organizationName') or existing_c.get('org_name', ''),
                'manual_star_level': c.get('manualStarLevel') or existing_c.get('manual_star_level'),
                'customer_success': c.get('customerSuccess') or existing_c.get('customer_success'),
                'technical_support': c.get('technicalSupport') or existing_c.get('technical_support'),
                'health_indicator': health,
                'im_type': existing_c.get('im_type'),
                'im_group_id': existing_c.get('im_group_id'),
                'im_group_url': existing_c.get('im_group_url'),
                'notes': existing_c.get('notes'),
                'address': existing_c.get('address'),
                'updated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
            })

        with open(CUSTOMERS_JSON, 'w', encoding='utf-8') as f:
            json.dump(customers, f, ensure_ascii=False, indent=2)

        # 2. 更新Worker JS
        total = len(customers)
        alert_count = sum(1 for c in customers if c.get('health_indicator') is not None and c['health_indicator'] >= 2.0)
        feishu_count = sum(1 for c in customers if c.get('im_type') == 'feishu')
        unset_count = sum(1 for c in customers if not c.get('im_type'))

        with open(MAIN_JS, 'r', encoding='utf-8') as f:
            content = f.read()
        customers_json = json.dumps(customers, ensure_ascii=False)
        cs = 'var _customers = '
        ce = content.index(cs) + len(cs)
        content = content[:ce] + customers_json + content[content.index(';', ce):]
        stats_json = json.dumps({'total': total, 'alert_count': alert_count, 'feishu_count': feishu_count, 'unset_count': unset_count}, ensure_ascii=False)
        ss = 'var _stats = '
        se = content.index(ss) + len(ss)
        content = content[:se] + stats_json + content[content.index(';', se):]
        with open(MAIN_JS, 'w', encoding='utf-8') as f:
            f.write(content)

        # 3. git push
        env = os.environ.copy()
        subprocess.run(['git', 'add', '-A'], cwd=REPO_DIR, env=env)
        subprocess.run(['git', 'commit', '-m', f'同步BOSS数据 {datetime.now().strftime("%Y-%m-%d %H:%M")}'], cwd=REPO_DIR, env=env)
        subprocess.run(['git', 'push', 'origin', 'main'], cwd=REPO_DIR, env=env)

        return {'ok': True, 'total': total, 'alert': alert_count, 'feishu': feishu_count, 'unset': unset_count}
    except Exception as e:
        return {'ok': False, 'msg': str(e)}
    finally:
        syncing = False

class Handler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/health':
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b'ok')
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        if self.path == '/sync':
            result = do_sync()
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(result).encode())
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, fmt, *args):
        print(f'[sync-server] {fmt % args}')

if __name__ == '__main__':
    print(f'启动同步服务 http://localhost:{PORT}')
    with socketserver.TCPServer(('', PORT), Handler) as httpd:
        httpd.serve_forever()

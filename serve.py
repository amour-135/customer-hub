import json, sqlite3, os, subprocess
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler

DB = 'C:/workspace/customer-hub/customers.db'
STATIC_DIR = 'C:/workspace/customer-hub'

def run_query(sql, args=()):
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    result = conn.execute(sql, args).fetchall()
    conn.close()
    return [dict(r) for r in result]

def run_boss(args):
    env = os.environ.copy()
    env['PYTHONIOENCODING'] = 'utf-8'
    r = subprocess.run(['boss-cli'] + args, capture_output=True, text=True, encoding='utf-8', env=env)
    try:
        return json.loads(r.stdout)
    except:
        return {'error': r.stdout + r.stderr}

def sync_from_boss():
    result = run_boss([
        'customer', 'list',
        '--filter', '{"signStatus":"已成交"}',
        '--fields', 'id,organizationUuid,organizationName,manualStarLevel,customerSuccess,technicalSupport,healthIndicator'
    ])
    if 'error' in result:
        return {'success': False, 'message': result['error']}
    orgs = result.get('data', {}).get('organizations', [])
    conn = sqlite3.connect(DB)
    count = 0
    for c in orgs:
        health = c.get('healthIndicator')
        if health is not None and health != '':
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
            c['id'],
            c.get('organizationUuid'),
            c['organizationName'],
            c.get('manualStarLevel'),
            c.get('customerSuccess'),
            c.get('technicalSupport'),
            health,
            datetime.now().isoformat()
        ))
        count += 1
    conn.execute('INSERT INTO sync_log (synced_at, count) VALUES (?, ?)', (datetime.now().isoformat(), count))
    conn.commit()
    conn.close()
    return {'success': True, 'count': count, 'message': f'同步了 {count} 条客户记录'}

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/' or self.path == '/index.html':
            self.serve_file('index.html')
        elif self.path == '/api/sync':
            result = sync_from_boss()
            self.respond(200, result)
        elif self.path.startswith('/api/customers'):
            keyword = health_filter = im_filter = None
            if '?' in self.path:
                path, qs = self.path.split('?', 1)
                self.path = path
                for pair in qs.split('&'):
                    if '=' not in pair: continue
                    k, v = pair.split('=', 1)
                    if k == 'keyword': keyword = v
                    if k == 'health': health_filter = v
                    if k == 'im_type': im_filter = v
            sql = 'SELECT boss_id,org_uuid,org_name,manual_star_level,customer_success,technical_support,health_indicator,im_type,im_group_id,im_group_url,notes,updated_at FROM customers WHERE 1=1'
            args = []
            if keyword:
                sql += ' AND org_name LIKE ?'
                args.append('%' + keyword + '%')
            if health_filter == 'alert':
                sql += ' AND health_indicator IS NOT NULL AND health_indicator >= 2.0'
            elif health_filter == 'ok':
                sql += ' AND (health_indicator IS NULL OR health_indicator < 2.0)'
            if im_filter:
                sql += ' AND im_type = ?'
                args.append(im_filter)
            sql += ' ORDER BY health_indicator DESC NULLS LAST, org_name'
            self.respond(200, run_query(sql, args))
        elif self.path == '/api/stats':
            conn = sqlite3.connect(DB)
            total = conn.execute('SELECT COUNT(*) FROM customers').fetchone()[0]
            alert = conn.execute('SELECT COUNT(*) FROM customers WHERE health_indicator >= 2.0').fetchone()[0]
            feishu = conn.execute("SELECT COUNT(*) FROM customers WHERE im_type='feishu'").fetchone()[0]
            unset = conn.execute('SELECT COUNT(*) FROM customers WHERE im_type IS NULL').fetchone()[0]
            last = conn.execute('SELECT synced_at,count FROM sync_log ORDER BY id DESC LIMIT 1').fetchone()
            conn.close()
            self.respond(200, {
                'total': total,
                'alert_count': alert,
                'feishu_count': feishu,
                'unset_count': unset,
                'last_synced': dict(zip(['synced_at','count'], last)) if last else None
            })
        elif self.path.startswith('/api/customers/'):
            parts = self.path.split('/')
            boss_id = int(parts[3].split('?')[0])
            data = run_query('SELECT * FROM customers WHERE boss_id=?', (boss_id,))
            self.respond(200, data[0] if data else {'error': 'not found'}, status=404 if not data else 200)
        else:
            self.serve_404()

    def do_POST(self):
        if self.path.startswith('/api/customers/'):
            parts = self.path.split('/')
            boss_id = int(parts[3])
            length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(length).decode('utf-8')
            params = {}
            for pair in body.split('&'):
                if '=' in pair:
                    k, v = pair.split('=', 1)
                    params[k] = v
            conn = sqlite3.connect(DB)
            conn.execute('UPDATE customers SET im_type=?,im_group_id=?,im_group_url=?,notes=?,updated_at=? WHERE boss_id=?',
                (params.get('im_type',''), params.get('im_group_id',''), params.get('im_group_url',''), params.get('notes',''),
                 datetime.now().isoformat(), boss_id))
            conn.commit()
            updated = conn.total_changes
            conn.close()
            self.respond(200, {'success': True, 'updated': updated > 0})
        else:
            self.respond(404, {'error': 'not found'})

    def serve_file(self, filename):
        path = os.path.join(STATIC_DIR, filename)
        if not os.path.exists(path):
            return self.serve_404()
        mime = 'text/html; charset=utf-8' if filename.endswith('.html') else 'application/octet-stream'
        self.send_response(200)
        self.send_header('Content-Type', mime)
        self.end_headers()
        with open(path, 'rb') as f:
            self.wfile.write(f.read())

    def serve_404(self):
        self.respond(404, {'error': 'not found'})

    def respond(self, code, data, status=None):
        self.send_response(code if status is None else status)
        self.send_header('Content-Control-Allow-Origin', '*')
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode('utf-8'))

if __name__ == '__main__':
    server = HTTPServer(('127.0.0.1', 8001), Handler)
    print('Customer Hub: http://127.0.0.1:8001')
    server.serve_forever()
import json, subprocess, os, sys
from datetime import datetime

REPO_DIR = os.path.dirname(os.path.abspath(__file__))
CUSTOMERS_JSON = os.path.join(REPO_DIR, 'customers.json')
MAIN_JS = os.path.join(REPO_DIR, 'actix-web', 'src', 'main.js')

def run_boss(args):
    env = os.environ.copy()
    env['PYTHONIOENCODING'] = 'utf-8'
    r = subprocess.run(args, capture_output=True, text=True, encoding='utf-8', env=env)
    return json.loads(r.stdout)

def sync_boss():
    print('同步BOSS数据...')
    try:
        data = run_boss(['boss-cli', 'customer', 'list',
            '--filter', '{"signStatus":"已成交"}',
            '--fields', 'id,organizationUuid,organizationName,manualStarLevel,customerSuccess,technicalSupport,healthIndicator'])
    except Exception as e:
        print(f'BOSS同步失败: {e}')
        print('跳过BOSS同步，使用现有customers.json')
        return False

    orgs = data['data']['organizations']
    print(f'获取到 {len(orgs)} 条客户数据')

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
            try:
                health = float(health)
            except:
                health = None
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
    print(f'写入 {len(customers)} 条到 customers.json')
    return True

def update_worker():
    print('更新Worker JS...')
    with open(CUSTOMERS_JSON, 'r', encoding='utf-8') as f:
        customers = json.load(f)

    total = len(customers)
    alert_count = sum(1 for c in customers if c.get('health_indicator') is not None and c['health_indicator'] >= 2.0)
    feishu_count = sum(1 for c in customers if c.get('im_type') == 'feishu')
    unset_count = sum(1 for c in customers if not c.get('im_type'))

    with open(MAIN_JS, 'r', encoding='utf-8') as f:
        content = f.read()

    # 替换 _customers 数据
    customers_json = json.dumps(customers, ensure_ascii=False)
    cs = 'var _customers = '
    ce = content.index(cs) + len(cs)
    semicolon = content.index(';', ce)
    content = content[:ce] + customers_json + content[semicolon:]

    # 替换 _stats 数据
    stats_json = json.dumps({'total': total, 'alert_count': alert_count, 'feishu_count': feishu_count, 'unset_count': unset_count}, ensure_ascii=False)
    ss = 'var _stats = '
    se = content.index(ss) + len(ss)
    semicolon2 = content.index(';', se)
    content = content[:se] + stats_json + content[semicolon2:]

    with open(MAIN_JS, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f'Worker已更新，总数={total} 告警={alert_count} 飞书={feishu_count} 未建联={unset_count}')

def git_push():
    print('推送到GitHub触发部署...')
    env = os.environ.copy()
    subprocess.run(['git', 'add', '-A'], cwd=REPO_DIR, env=env)
    result = subprocess.run(['git', 'diff', '--staged', '--stat'], capture_output=True, text=True, cwd=REPO_DIR, env=env)
    if not result.stdout.strip():
        print('没有变更，无需推送')
        return
    print(result.stdout)
    msg = f'同步BOSS数据 {datetime.now().strftime("%Y-%m-%d %H:%M")}'
    subprocess.run(['git', 'commit', '-m', msg], cwd=REPO_DIR, env=env)
    subprocess.run(['git', 'push', 'origin', 'main'], cwd=REPO_DIR, env=env)
    print('推送完成，GitHub Actions将在约30秒后完成部署')

if __name__ == '__main__':
    changed = sync_boss()
    update_worker()
    git_push()
    print('全部完成')

import json, re

with open('C:/workspace/customer-hub/customers.json', 'r', encoding='utf-8') as f:
    customers = json.load(f)

total = len(customers)
alert = sum(1 for c in customers if c.get('health_indicator') is not None and c['health_indicator'] >= 2.0)
feishu = sum(1 for c in customers if c.get('im_type') == 'feishu')
unset = sum(1 for c in customers if not c.get('im_type'))

with open('C:/workspace/customer-hub/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Find the <script> tag and replace everything inside it with our clean version
script_start = html.find('<script>')
script_end = html.find('</script>')
if script_start < 0 or script_end < 0:
    print('ERROR: no script tag found')
    exit(1)

new_script = '''
var _customers = ''' + json.dumps(customers, ensure_ascii=False) + ''';
var _stats = ''' + json.dumps({'total': total, 'alert_count': alert, 'feishu_count': feishu, 'unset_count': unset}, ensure_ascii=False) + ''';

function loadStats() {
    document.getElementById('statTotal').textContent = _stats.total || 0;
    document.getElementById('statAlert').textContent = _stats.alert_count || 0;
    document.getElementById('statOk').textContent = (_stats.total || 0) - (_stats.alert_count || 0);
    document.getElementById('statFeishu').textContent = _stats.feishu_count || 0;
    document.getElementById('statUnset').textContent = _stats.unset_count || 0;
}

function loadData() {
    var kw = document.getElementById('searchInput').value.trim();
    var hf = document.getElementById('healthFilter').value;
    var im = document.getElementById('imFilter').value;
    document.getElementById('loading').style.display = 'block';
    document.getElementById('table').style.display = 'none';
    document.getElementById('empty').style.display = 'none';
    var data = _customers.filter(function(c) {
        if (kw && !(c.org_name && c.org_name.indexOf(kw) >= 0)) return false;
        if (hf === 'alert' && !(c.health_indicator != null && c.health_indicator >= 2.0)) return false;
        if (hf === 'ok' && (c.health_indicator == null || c.health_indicator < 2.0)) return false;
        if (im && c.im_type !== im) return false;
        return true;
    });
    document.getElementById('loading').style.display = 'none';
    if (!data.length) {
        document.getElementById('empty').style.display = 'block';
        return;
    }
    var tbody = document.getElementById('tbody');
    tbody.innerHTML = data.map(function(c) {
        var star = c.manual_star_level ? '<span class="star">' + '\\u2605'.repeat(c.manual_star_level) + '</span>' : '\\u2014';
        var health = c.health_indicator != null ? parseFloat(c.health_indicator) : null;
        var healthCls = health !== null && health >= 2.0 ? 'alert' : (health !== null ? 'ok' : '');
        var healthTxt = health !== null ? health.toFixed(1) : '\\u2014';
        var cs = c.customer_success || '\\u2014';
        return '<tr>' +
            '<td><div class="cs-name">' + esc(c.org_name || '') + '</div></td>' +
            '<td>' + star + '</td>' +
            '<td><span class="health ' + healthCls + '">' + healthTxt + '</span></td>' +
            '<td>' + esc(cs) + '</td>' +
            '<td>' + renderBadge(c.im_type) + '</td>' +
            '<td>' + renderJumpBtn(c.im_type, c.im_group_id, c.im_group_url) + '</td>' +
        '</tr>';
    }).join('');
    document.getElementById('table').style.display = 'table';
}

function syncAndReload() { window.location.reload(); }

function renderBadge(type) {
    if (type === 'feishu') return '<span class="badge badge-feishu">\\u98de\\u4e66</span>';
    if (type === 'dingtalk') return '<span class="badge badge-dingtalk">\\u9489\\u9489</span>';
    if (type === 'wxwork') return '<span class="badge badge-wxwork">\\u4f01\\u5fae</span>';
    return '<span class="badge badge-none">\\u672a\\u8bbe\\u7f6e</span>';
}

function renderJumpBtn(type, groupId, groupUrl) {
    if (!type || !groupId) return '<span class="btn-jump btn-unset">\\u672a\\u914d\\u7f6e</span>';
    var url = groupUrl || makeDeepLink(type, groupId);
    var label = type === 'feishu' ? '\\u98de\\u4e66' : type === 'dingtalk' ? '\\u9489\\u9489' : type === 'wxwork' ? '\\u4f01\\u5fae' : '\\u8df3\\u8f6c';
    var cls = type === 'feishu' ? 'btn-feishu' : type === 'dingtalk' ? 'btn-dingtalk' : type === 'wxwork' ? 'btn-wxwork' : 'btn-unset';
    return '<a class="btn-jump ' + cls + '" href="' + esc(url) + '" target="_blank">' + label + '\\u7fa4</a>';
}

function makeDeepLink(type, groupId) {
    if (!groupId) return null;
    if (type === 'feishu') return 'https://applink.feishu.cn/client/chat/open?openChatId=' + groupId;
    if (type === 'dingtalk') return 'dingtalk://dingtalkclient/action/openconversation?cid=' + groupId;
    if (type === 'wxwork') return 'wxwork://message?conversationid=' + groupId;
    return null;
}

function esc(s) {
    if (s == null) return '';
    return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/""/g,'&quot;');
}

loadStats();
loadData();
'''

html = html[:script_start + 8] + new_script + html[script_end:]

with open('C:/workspace/customer-hub/index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print('Done, size:', len(html))
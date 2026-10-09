<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>客户建联中台</title>
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: #f5f6fa; color: #1a1a2e; font-size: 14px; }
  .header { background: #1a1a2e; color: #fff; padding: 20px 32px; display: flex; align-items: center; justify-content: space-between; }
  .header h1 { font-size: 18px; font-weight: 600; }
  .header .meta { font-size: 12px; color: #8888aa; }
  .stats { display: flex; gap: 24px; padding: 16px 32px; background: #fff; border-bottom: 1px solid #eee; }
  .stat { display: flex; flex-direction: column; }
  .stat .num { font-size: 24px; font-weight: 700; color: #1a1a2e; }
  .stat .label { font-size: 12px; color: #888; }
  .stat.alert .num { color: #e74c3c; }
  .stat.ok .num { color: #27ae60; }
  .stat.im .num { color: #1a73e8; }
  .toolbar { padding: 16px 32px; display: flex; gap: 12px; align-items: center; background: #fff; border-bottom: 1px solid #eee; flex-wrap: wrap; }
  .toolbar input { padding: 8px 12px; border: 1px solid #ddd; border-radius: 6px; font-size: 13px; width: 200px; outline: none; }
  .toolbar input:focus { border-color: #4a4a8a; }
  .toolbar select { padding: 8px 12px; border: 1px solid #ddd; border-radius: 6px; font-size: 13px; outline: none; }
  .badge { display: inline-block; padding: 2px 8px; border-radius: 4px; font-size: 11px; font-weight: 600; }
  .badge-feishu { background: #e8f0fe; color: #1a73e8; }
  .badge-dingtalk { background: #e0f7fa; color: #0097a7; }
  .badge-wxwork { background: #e8f5e9; color: #388e3c; }
  .badge-none { background: #f5f5f5; color: #999; }
  .star { color: #f5c518; font-size: 12px; }
  .health-high { color: #e74c3c; font-weight: 600; }
  .health-mid { color: #f39c12; font-weight: 600; }
  .health-ok { color: #27ae60; }
  .btn-jump { padding: 4px 10px; border-radius: 4px; font-size: 11px; font-weight: 600; text-decoration: none; display: inline-block; border: none; cursor: pointer; transition: opacity 0.2s; }
  .btn-jump:hover { opacity: 0.8; }
  .btn-feishu { background: #1a73e8; color: #fff; }
  .btn-dingtalk { background: #0097a7; color: #fff; }
  .btn-wxwork { background: #388e3c; color: #fff; }
  .btn-unset { background: #ddd; color: #888; }
  .table-wrap { padding: 0 32px 32px; }
  table { width: 100%; border-collapse: collapse; background: #fff; border-radius: 8px; overflow: hidden; box-shadow: 0 1px 3px rgba(0,0,0,0.06); }
  th { background: #f8f9fc; padding: 12px 16px; text-align: left; font-size: 12px; font-weight: 600; color: #888; border-bottom: 1px solid #eee; }
  td { padding: 12px 16px; border-bottom: 1px solid #f0f0f0; vertical-align: middle; }
  tr:last-child td { border-bottom: none; }
  tr:hover td { background: #fafbff; }
  .name-cell { font-weight: 500; max-width: 280px; }
  .tag-row { display: flex; gap: 4px; align-items: center; flex-wrap: wrap; }
  .loading { text-align: center; padding: 40px; color: #888; }
  .empty { text-align: center; padding: 40px; color: #aaa; }
  .refresh-btn { padding: 8px 16px; background: #4a4a8a; color: #fff; border: none; border-radius: 6px; font-size: 13px; cursor: pointer; }
  .refresh-btn:hover { background: #3a3a6a; }
  .last-sync { font-size: 11px; color: #888; }
  .badge-count { display: inline-block; background: #e74c3c; color: #fff; border-radius: 10px; padding: 1px 6px; font-size: 10px; margin-left: 4px; }
</style>
</head>
<body>

<div class="header">
  <div>
    <h1>客户建联中台</h1>
    <div class="meta">技术支持 · 沐宸</div>
  </div>
  <div class="last-sync" id="lastSync"></div>
</div>

<div class="stats" id="stats">
  <div class="stat"><div class="num" id="statTotal">—</div><div class="label">客户总数</div></div>
  <div class="stat alert"><div class="num" id="statAlert">—</div><div class="label">健康度告警</div></div>
  <div class="stat ok"><div class="num" id="statOk">—</div><div class="label">健康</div></div>
  <div class="stat im"><div class="num" id="statFeishu">—</div><div class="label">已建联(飞书)</div></div>
  <div class="stat"><div class="num" id="statUnset">—</div><div class="label">未建联</div></div>
</div>

<div class="toolbar">
  <input type="text" id="searchInput" placeholder="搜索客户名称…" oninput="loadData()">
  <select id="healthFilter" onchange="loadData()">
    <option value="">全部健康度</option>
    <option value="alert">告警 (≥2.0)</option>
    <option value="ok">健康 (&lt;2.0)</option>
  </select>
  <select id="imFilter" onchange="loadData()">
    <option value="">全部建联方式</option>
    <option value="feishu">飞书</option>
    <option value="dingtalk">钉钉</option>
    <option value="wxwork">企微</option>
  </select>
  <button class="refresh-btn" onclick="loadData()">刷新</button>
</div>

<div class="table-wrap">
  <div id="loading" class="loading">加载中…</div>
  <div id="empty" class="empty" style="display:none">没有匹配的客户</div>
  <table id="table" style="display:none">
    <thead>
      <tr>
        <th>客户名称</th>
        <th>星级</th>
        <th>健康度</th>
        <th>客户成功经理</th>
        <th>建联方式</th>
        <th>跳转</th>
      </tr>
    </thead>
    <tbody id="tbody"></tbody>
  </table>
</div>

<script>
const API = "http://127.0.0.1:8001";
let allCustomers = [];

async function loadData() {
  const kw = document.getElementById("searchInput").value.trim();
  const health = document.getElementById("healthFilter").value;
  const imType = document.getElementById("imFilter").value;

  document.getElementById("loading").style.display = "block";
  document.getElementById("table").style.display = "none";
  document.getElementById("empty").style.display = "none";

  try {
    const [customersRes, statsRes] = await Promise.all([
      fetch(buildCustomerUrl(kw, health, imType)),
      fetch(API + "/api/stats")
    ]);
    const customers = await customersRes.json();
    const stats = await statsRes.json();
    allCustomers = customers;
    renderStats(stats);
    renderTable(customers);
    document.getElementById("lastSync").textContent = stats.last_synced ? "最后同步：" + stats.last_synced.synced_at : "";
  } catch(e) {
    document.getElementById("loading").textContent = "API 未响应，请确保启动.bat已运行";
  }
}

function buildCustomerUrl(kw, health, imType) {
  const params = [];
  if (kw) params.push("keyword=" + encodeURIComponent(kw));
  if (health) params.push("health=" + encodeURIComponent(health));
  if (imType) params.push("im_type=" + encodeURIComponent(imType));
  return API + "/api/customers" + (params.length ? "?" + params.join("&") : "");
}

function renderStats(stats) {
  document.getElementById("statTotal").textContent = stats.total || 0;
  document.getElementById("statAlert").textContent = stats.alert_count || 0;
  document.getElementById("statOk").textContent = (stats.total || 0) - (stats.alert_count || 0);
  document.getElementById("statFeishu").textContent = stats.feishu_count || 0;
  document.getElementById("statUnset").textContent = stats.unset_count || 0;
}

function renderTable(customers) {
  const tbody = document.getElementById("tbody");
  const table = document.getElementById("table");
  const loading = document.getElementById("loading");
  const empty = document.getElementById("empty");
  loading.style.display = "none";
  if (!customers || customers.length === 0) { table.style.display = "none"; empty.style.display = "block"; return; }
  empty.style.display = "none";
  table.style.display = "table";
  tbody.innerHTML = customers.map(c => {
    const stars = renderStars(c.manual_star_level);
    const health = renderHealth(c.health_indicator);
    const imBadge = renderImBadge(c.im_type);
    const jumpBtn = renderJumpBtn(c.im_type, c.im_group_id, c.im_group_url);
    return "<tr>" +
      "<td class='name-cell'>" + esc(c.org_name || "—") + "</td>" +
      "<td>" + stars + "</td>" +
      "<td>" + health + "</td>" +
      "<td>" + esc(c.customer_success || "—") + "</td>" +
      "<td>" + imBadge + "</td>" +
      "<td>" + jumpBtn + "</td>" +
      "</tr>";
  }).join("");
}

function renderStars(level) {
  if (!level) return "<span style='color:#ddd'>☆☆☆☆☆</span>";
  const n = parseInt(level);
  return "<span class='star'>" + "★".repeat(n) + "☆".repeat(5-n) + "</span>";
}

function renderHealth(v) {
  if (v === null || v === undefined || v === "") return "<span style='color:#bbb'>—</span>";
  if (v >= 2.0) return "<span class='health-high'>" + v + "</span>";
  if (v >= 1.0) return "<span class='health-mid'>" + v + "</span>";
  return "<span class='health-ok'>" + v + "</span>";
}

function renderImBadge(type) {
  if (type === "feishu") return "<span class='badge badge-feishu'>飞书</span>";
  if (type === "dingtalk") return "<span class='badge badge-dingtalk'>钉钉</span>";
  if (type === "wxwork") return "<span class='badge badge-wxwork'>企微</span>";
  return "<span class='badge badge-none'>未设置</span>";
}

function renderJumpBtn(type, groupId, groupUrl) {
  if (!type || !groupId) return "<span class='btn-jump btn-unset'>未配置</span>";
  const url = groupUrl || makeDeepLink(type, groupId);
  const label = type === "feishu" ? "飞书" : type === "dingtalk" ? "钉钉" : type === "wxwork" ? "企微" : "跳转";
  const cls = type === "feishu" ? "btn-feishu" : type === "dingtalk" ? "btn-dingtalk" : type === "wxwork" ? "btn-wxwork" : "btn-unset";
  return "<a class='btn-jump " + cls + "' href='" + esc(url) + "' target='_blank'>" + label + "群</a>";
}

function makeDeepLink(type, groupId) {
  if (!groupId) return null;
  if (type === "feishu") return "https://applink.feishu.cn/client/chat/open?openChatId=" + groupId;
  if (type === "dingtalk") return "dingtalk://dingtalkclient/action/openconversation?cid=" + groupId;
  if (type === "wxwork") return "wxwork://message?conversationid=" + groupId;
  return null;
}

function esc(s) {
  if (s === null || s === undefined) return "";
  return String(s).replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;").replace(/"/g,"&quot;");
}

loadData();
setInterval(loadData, 60000);
</script>
</body>
</html>

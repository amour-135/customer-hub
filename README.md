# 客户建联中台

本地轻量中台，零云依赖，数据全在你电脑里。

## 数据源
- 影刀 BOSS 系统（只读同步）
- 当前用户：（已登录）
- 已同步：66 家已成交客户

## 健康度说明
健康度数值来源于 BOSS 系统，`health_indicator` 字段：
- 低于 2.0：健康（绿色）
- 2.0 及以上：需关注（红色）

## 启动

双击 `启动.bat`，等待两个服务就绪后访问：
- API 地址：http://127.0.0.1:8001

## API 接口

| 接口 | 说明 |
|------|------|
| `GET /api/customers` | 全部客户列表 |
| `GET /api/customers?health=alert` | 仅健康度告警客户 |
| `GET /api/customers?health=ok` | 仅健康客户 |
| `GET /api/customers?keyword=杭州` | 按名称搜索 |
| `GET /api/customers/{boss_id}` | 单个客户详情 |
| `GET /api/stats` | 统计信息 |
| `POST /api/customers/{boss_id}/im` | 更新客户的IM建联信息 |

## 影刀 AI Weave 接入方式

在 Weave 里创建一个「自定义数据源」类型块，URL 填：
```
http://127.0.0.1:8001/api/customers
```

Weave 表格绑定字段对应关系：
- `org_name` → 客户名称
- `health_indicator` → 健康度（数字）
- `manual_star_level` → 星级
- `customer_success` → 客户成功经理
- `technical_support` → 技术支持
- `im_type` → 建联方式（feishu/dingtalk/wxwork）
- `im_group_id` → 群ID（用于跳转链接）
- `notes` → 备注

## IM 跳转链接格式（供手动填入）

### 飞书群
`https://applink.feishu.cn/client/imconversation/?openChatId={群ID}`

### 钉钉群
`dingtalk://dingtalkclient/action/openconversation?cid={群ID}`

### 企业微信群
`wxwork://message?corpid={corpid}&conversationid={群ID}`

## 数据同步

- 每次双击 `启动.bat` 自动增量同步（根据 boss_id 去重）
- 如需强制全量刷新，删除 `customers.db` 后重新启动

## 目录结构

```
customer-hub/
  customers.db      # SQLite 数据库
  serve.py          # HTTP API 服务
  scripts/
    sync_boss.py    # BOSS 数据同步脚本
  启动.bat          # 一键启动脚本
  README.md
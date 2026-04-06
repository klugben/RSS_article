# 技术架构

> 项目: RSS_article
> 状态: 已确认

## 架构概要

```
┌──────────────────────────────────────────────────────────────┐
│                      腾讯云 Ubuntu 24.04                      │
│                                                              │
│  ┌──────────┐    ┌───────────┐    ┌───────────────────────┐  │
│  │  lumen   │    │ feeds.db  │    │  OpenClaw Gateway     │  │
│  │ (Rust)   │───▶│ (SQLite)  │◀──│                       │  │
│  │ RSS 抓取 │    │           │    │  ┌─────────────────┐  │  │
│  └──────────┘    │ ┌───────┐ │    │  │ RSS_article     │  │  │
│       ▲          │ │articles│ │    │  │ Agent           │  │  │
│       │          │ │ feeds  │ │    │  │                 │  │  │
│       │          │ └───┬───┘ │    │  │ ┌─────────────┐ │  │  │
│    RSS Feeds     │     │     │    │  │ │ SOUL.md     │ │  │  │
│                   │     │     │    │  │ │ USER.md     │ │  │  │
│                   └─────┼─────┘    │  │ └─────────────┘ │  │  │
│                         │          │  │                 │  │  │
│                         │ 只读查询  │  │ SQL ──▶ 分类   │  │  │
│                         ├─────────▶│  │ 摘要 ──▶ 推送   │  │  │
│                         │          │  └────────┬────────┘  │  │
│                         │          │           │            │  │
│  ┌──────────┐          │          │  ┌────────▼────────┐  │  │
│  │digest.db│◀─────────┘          │  │ OpenClaw CLI    │  │  │
│  │(去重记录)│   写入已推送 ID      │  │ message send    │  │  │
│  └──────────┘                     │  └────────┬────────┘  │  │
│                                   └───────────┼───────────┘  │
│                                               │               │
└───────────────────────────────────────────────┼───────────────┘
                                                │
                                                │ Feishu API
                                                ▼
                                       ┌──────────────┐
                                       │  飞书群组     │
                                       │  简报消息     │
                                       └──────────────┘
```

## 组件职责

### 1. lumen（外部组件）

| 项目 | 说明 |
|------|------|
| 语言 | Rust |
| 职责 | RSS 抓取、文章存储、全文搜索 |
| 交互 | 独立运行，通过 feeds.db 与 Agent 间接通信 |
| 调度 | 系统级 cron 或 systemd timer（与 Agent 无关） |
| 数据 | 写入 articles / feeds 表 |

### 2. feeds.db（共享存储）

| 项目 | 说明 |
|------|------|
| 类型 | SQLite（WAL 模式） |
| 所有者 | lumen |
| Agent 权限 | 只读 SELECT |
| 并发 | WAL 模式支持读写并发，只读查询不阻塞写入 |

### 3. digest.db（Agent 专属）

| 项目 | 说明 |
|------|------|
| 类型 | SQLite |
| 所有者 | RSS_article Agent |
| 用途 | 推送去重（pushed_articles 表） |
| 生命周期 | Agent 首次运行时自动创建 |

### 4. OpenClaw Gateway + Agent

| 项目 | 说明 |
|------|------|
| 职责 | Cron 调度、Agent 执行环境、CLI 路由 |
| Agent 输入 | SOUL.md（行为规则）+ USER.md（运行时配置） |
| Agent 能力 | SQL 查询、主题分类、摘要生成、消息推送 |
| 触发方式 | Cron（每日 8:00）或手动（openclaw agents run） |

### 5. OpenClaw CLI（消息通道）

| 项目 | 说明 |
|------|------|
| 命令 | `openclaw message send` |
| 协议 | 飞书 Bot API（通过 OpenClaw 封装） |
| 输出 | 飞书群组文本消息 |

## 数据流

```
Phase 1: 数据采集（lumen 独立完成）
  RSS Feed ──lumen fetch──▶ feeds.db

Phase 2: 信息处理（Agent 核心职责）
  feeds.db ──SELECT──▶ Agent 内存
                          │
                    ┌─────┴──────┐
                    │ 按 feed_id │
                    │ 分组       │
                    └─────┬──────┘
                          │
                    ┌─────┴──────┐
                    │ 主题分类   │
                    │ TOPIC_RULES│
                    └─────┬──────┘
                          │
                    ┌─────┴──────┐
                    │ 摘要生成   │
                    │ ≤400 字    │
                    └─────┬──────┘
                          │
Phase 3: 推送交付
                          │
                    openclaw message send
                          │
                          ▼
                    飞书群组消息
                          │
                    ┌─────┴──────┐
                    │ 记录去重   │
                    │ digest.db  │
                    └────────────┘
```

## 部署架构

```
┌─────────────────────────────────────────────┐
│  腾讯云服务器                                │
│  Ubuntu 24.04                               │
│                                             │
│  /root/tencent_rsync_mac/RSS_article/       │
│  ├── lumen/                 # lumen 二进制   │
│  ├── lumen-data/feeds.db    # 文章数据库     │
│  ├── lumen-data/digest.db   # 去重数据库     │
│  ├── export_lumen_to_output.py               │
│  └── run_rss_export.sh                      │
│                                             │
│  /root/.openclaw/                           │
│  ├── gateway                 # OpenClaw GW   │
│  └── workspace-RSS_article/                 │
│      ├── SOUL.md             # Agent 行为    │
│      └── USER.md             # 运行时配置    │
│                                             │
│  系统服务:                                   │
│  ├── lumen fetch (cron)     # RSS 抓取      │
│  └── OpenClaw Gateway       # Agent 宿主    │
│      └── Cron: 0 8 * * *   # 每日简报       │
└─────────────────────────────────────────────┘
```

## 错误处理策略

| 错误类型 | 处理方式 | 用户感知 |
|---------|---------|---------|
| feeds.db 不存在 | 终止流程，输出错误日志 | 无简报 |
| digest.db 不存在 | 自动创建 | 无感知 |
| SQL 查询失败 | 终止流程，输出错误日志 | 无简报 |
| 飞书推送失败 | 跳过该 feed，不记录去重 | 无简报（下次重试） |
| 摘要超 400 字 | Agent 内部压缩重试 | 无感知 |
| SQLite BUSY | 等待 1 秒重试，最多 3 次 | 无感知 |

## 安全考虑

| 风险 | 措施 |
|------|------|
| DB_PATH 注入 | 路径硬编码在 USER.md，不接受用户输入 |
| SQL 注入 | Agent 使用参数化查询（非拼接 SQL） |
| chat_id 泄露 | USER.md 不纳入版本控制（在 source/ 目录） |
| 飞书 Bot 权限 | allowlist 策略限制可访问群组 |

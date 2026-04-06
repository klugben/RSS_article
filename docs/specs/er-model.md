# ER 模型设计

> 项目: RSS_article
> 状态: 已确认

## 数据库总览

系统使用 **两个 SQLite 数据库**：

| 数据库 | 所有者 | Agent 操作 | 说明 |
|--------|--------|-----------|------|
| feeds.db | lumen (Rust) | **只读** | RSS 文章存储，lumen 管理 schema |
| digest.db | RSS_article Agent | **读写** | 简报去重与推送记录，Agent 自管理 |

## 一、feeds.db（只读，lumen 管理）

Agent 仅执行 SELECT，不修改任何表。

### 核心表

#### articles（文章）

lumen 核心表，Agent 的主要数据来源。

| 字段 | 类型 | Agent 用途 | 说明 |
|------|------|-----------|------|
| id | INTEGER PK | 去重标识 | 文章唯一 ID |
| feed_id | INTEGER FK | 订阅源分组 | → feeds.id |
| title | TEXT | 摘要输入 | 文章标题 |
| url | TEXT | 原文链接 | 可能为 NULL |
| content | TEXT | 摘要输入 | 摘要内容（可能为空） |
| summary | TEXT | 摘要输入 | AI 生成摘要 |
| published_at | TEXT | 时间窗口过滤 | ISO 8601，UTC |
| is_read | INTEGER | — | 不使用 |
| is_starred | INTEGER | — | 不使用 |
| fetched_at | TEXT | — | 不使用 |
| full_content | TEXT | 摘要输入（首选） | 全文内容 |
| guid | TEXT | 辅助去重 | feed 内唯一标识 |
| tags | TEXT | 辅助分类 | 逗号分隔标签 |
| tldr | TEXT | 摘要辅助 | lumen 生成的 TLDR |

#### feeds（订阅源）

| 字段 | 类型 | Agent 用途 | 说明 |
|------|------|-----------|------|
| id | INTEGER PK | 文章分组 | 订阅源 ID |
| title | TEXT | 简报标题 | 订阅源名称 |
| url | TEXT | — | RSS feed 地址 |

### 辅助表（Agent 不使用）

- `entities` — 实体抽取（lumen 内部使用）
- `folders` / `folder_feeds` — 文件夹分类
- `articles_fts` — 全文搜索索引
- `rejected_suggestions` / `reset_reasons` — lumen 内部状态
- `_meta` — lumen 元数据

## 二、digest.db（读写，Agent 自管理）

Agent 在首次运行时自动创建，用于记录推送历史。

### pushed_articles（已推送记录）

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | INTEGER | PK AUTOINCREMENT | 记录 ID |
| article_id | INTEGER | NOT NULL | → articles.id（feeds.db） |
| feed_id | INTEGER | NOT NULL | → feeds.id（feeds.db） |
| pushed_at | TEXT | NOT NULL | 推送时间（ISO 8601） |
| | | UNIQUE(article_id) | 防止重复推送 |

**建表 SQL**：

```sql
CREATE TABLE IF NOT EXISTS pushed_articles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    article_id INTEGER NOT NULL,
    feed_id INTEGER NOT NULL,
    pushed_at TEXT NOT NULL DEFAULT (datetime('now')),
    UNIQUE(article_id)
);
```

## ER 关系图

```
┌─────────────┐          ┌─────────────────┐
│   feeds     │ 1      N │   articles      │
│ (feeds.db)  │─────────▶│  (feeds.db)     │
│             │          │                 │
│ id (PK)     │          │ id (PK)         │
│ title       │          │ feed_id (FK)    │
│ url         │          │ title           │
│             │          │ url             │
│             │          │ content         │
│             │          │ full_content    │
│             │          │ summary         │
│             │          │ published_at    │
│             │          │ guid            │
│             │          │ tags            │
│             │          │ tldr            │
└─────────────┘          └────────┬────────┘
                                  │
                                  │ 1:1 (推送后记录)
                                  │
                         ┌────────▼────────┐
                         │ pushed_articles │
                         │  (digest.db)    │
                         │                 │
                         │ article_id (UQ) │
                         │ feed_id         │
                         │ pushed_at       │
                         └─────────────────┘
```

## Agent 数据流

```
feeds.db (只读)                    digest.db (读写)
┌──────────────┐                   ┌──────────────┐
│  SELECT      │                   │  INSERT      │
│  articles    │──▶ 分类+摘要 ──▶  │  pushed_     │
│  WHERE       │   (Agent 内存)    │  articles    │
│  24h 窗口    │                   │              │
│  NOT IN      │◀── 查询已推送 ──  │  SELECT      │
│  pushed      │                   │  去重过滤     │
└──────────────┘                   └──────────────┘
```

## 数据一致性说明

1. **跨库引用**：`pushed_articles.article_id` 引用 `articles.id`，但分属不同数据库，无外键约束，由应用层保证一致性
2. **feeds.db 变更安全**：lumen 可能删除旧文章（CASCADE），pushed_articles 中的残留记录不影响业务（仅用于去重，无匹配即跳过）
3. **digest.db 位置**：与 feeds.db 同目录，路径通过环境变量或配置注入

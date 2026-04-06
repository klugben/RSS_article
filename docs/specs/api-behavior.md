# API 行为设计

> 项目: RSS_article
> 状态: 已确认

## 设计说明

本项目无传统 REST API。Agent 通过以下三种接口与外部系统交互：

1. **SQLite SQL** — 数据查询与去重记录
2. **OpenClaw CLI** — 消息推送
3. **OpenClaw Cron** — 定时调度

## 一、SQLite 接口

### 1.1 查询最近 24 小时新文章（含去重）

```sql
-- 输入参数: 无（时间窗口硬编码 24h）
-- 预期: 按订阅源分组返回未推送文章

SELECT
    a.id,
    a.title,
    a.url,
    a.published_at,
    COALESCE(a.full_content, a.content, a.summary, '') AS body,
    f.title AS feed_title,
    f.id AS feed_id
FROM articles a
JOIN feeds f ON f.id = a.feed_id
WHERE a.published_at >= datetime('now', '-1 day')
  AND a.id NOT IN (
      SELECT article_id FROM pushed_articles
  )
ORDER BY f.id, a.published_at DESC;
```

**行为契约**：

| 项目 | 说明 |
|------|------|
| 隔离级别 | 只读（feeds.db），不加锁 |
| 时区 | published_at 为 UTC，Agent 负责转换为北京时间显示 |
| 空结果 | 返回空集 → Agent 跳过推送，不发送消息 |
| 错误处理 | DB 不存在或查询失败 → 输出错误日志，终止流程 |

### 1.2 记录已推送文章

```sql
-- 输入参数: article_id, feed_id
-- 副作用: 写入 digest.db

INSERT OR IGNORE INTO pushed_articles (article_id, feed_id, pushed_at)
VALUES (?, ?, datetime('now'));
```

**行为契约**：

| 项目 | 说明 |
|------|------|
| 幂等性 | UNIQUE(article_id) + INSERT OR IGNORE，重复插入不报错 |
| 数据库 | digest.db（独立于 feeds.db） |
| 批量 | 推送成功后批量插入该次推送的所有 article_id |

### 1.3 初始化去重表

```sql
-- 首次运行时自动执行

CREATE TABLE IF NOT EXISTS pushed_articles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    article_id INTEGER NOT NULL,
    feed_id INTEGER NOT NULL,
    pushed_at TEXT NOT NULL DEFAULT (datetime('now')),
    UNIQUE(article_id)
);
```

## 二、OpenClaw CLI 接口

### 2.1 飞书消息推送

```bash
# 输入参数:
#   --message: 简报文本（≤400 字，Markdown 格式）
#   --target: 飞书群组 chat_id
# 输出: 推送结果（成功/失败）

openclaw message send \
  --channel feishu \
  --target "chat:oc_97c792a037da30fe0e1079e4b63f4bf7" \
  --message "<简报内容>"
```

**行为契约**：

| 项目 | 说明 |
|------|------|
| 格式 | 纯文本 Markdown（飞书群消息不支持卡片） |
| 长度 | ≤400 字（Agent 负责截断，CLI 不做限制） |
| 频率 | 每源每日最多 1 条（去重保证） |
| 错误 | 推送失败 → 不记录 pushed_articles，下次重试 |

### 2.2 Agent 手动触发

```bash
# 无参数触发，执行完整推送流程
openclaw agents run RSS_article
```

**行为契约**：与 Cron 触发执行完全相同的逻辑。

### 2.3 Cron 定时调度

```bash
# 注册 Cron 任务（一次性配置）
openclaw cron create \
  --agent RSS_article \
  --channel feishu \
  --to "chat:oc_97c792a037da30fe0e1079e4b63f4bf7" \
  --cron "0 8 * * *" \
  --timeout 300 \
  --prompt "执行每日 RSS 简报采集与推送"
```

**行为契约**：

| 项目 | 说明 |
|------|------|
| 调度 | 每日 08:00（服务器本地时间） |
| 超时 | 300 秒 |
| 重试 | Gateway 异常时不自动重试，需人工介入 |

## 三、Agent 内部行为接口

### 3.1 主题分类

```
输入: 文章 title + body
输出: 主题标签（字符串）
规则: TOPIC_RULES 关键词匹配，取最高分
兜底: "未分类"
```

### 3.2 摘要生成

```
输入: 按主题分组的文章列表 + 文章数量
输出: 简报文本（≤400 字）
规则:
  - ≤3 篇: 逐篇摘要 + 原文链接
  - >3 篇: 要点概括 + 全部链接列表
约束: 不编造、不评价、忠于原文
```

## 接口调用序列

```
Cron / Manual Trigger
        │
        ▼
  [SQLite] SELECT 未推送文章
        │
     空集? ──Yes──▶ [结束，不推送]
        │ No
        ▼
  [Agent] 按 feed_id 分组
        │
        ▼
  FOR EACH feed:
        │
        ▼
    [Agent] 主题分类 + 摘要生成（≤400字）
        │
        ▼
    [CLI] openclaw message send
        │
     成功? ──No──▶ [跳过该 feed，记录错误]
        │ Yes
        ▼
    [SQLite] INSERT pushed_articles（批量）
        │
        ▼
    NEXT feed
        │
        ▼
  [结束]
```

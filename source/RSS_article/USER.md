# RSS_article — 运行时配置

> 此文件部署到云端 Agent workspace：`/root/.openclaw/workspace-RSS_article/`

## 数据源

### feeds.db（只读，lumen 管理）

```bash
# 数据库路径
DB_PATH=/root/.local/share/lumen/feeds.db
```

```sql
-- 先 ATTACH digest.db（跨库去重查询的前置步骤，每次查询前必须执行）
ATTACH '/root/.local/share/lumen/digest.db' AS digest;

-- 查询最近 24 小时未推送文章（含去重过滤）
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
      SELECT article_id FROM digest.pushed_articles
  )
ORDER BY f.id, a.published_at DESC;
```

**说明**：
- `published_at` 为 UTC 时间，显示时需转换为北京时间（+8h）
- `body` 通过 COALESCE 优先取 full_content → content → summary
- `NOT IN pushed_articles` 跨库查询 digest.db 实现去重
- 按 `f.id` 分组排序，确保同一订阅源文章连续

### digest.db（读写，Agent 自管理）

```bash
# 去重数据库路径（与 feeds.db 同目录）
DIGEST_DB_PATH=/root/.local/share/lumen/digest.db
```

```sql
-- 首次运行时自动初始化（CREATE IF NOT EXISTS，幂等）
CREATE TABLE IF NOT EXISTS pushed_articles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    article_id INTEGER NOT NULL,
    feed_id INTEGER NOT NULL,
    pushed_at TEXT NOT NULL DEFAULT (datetime('now')),
    UNIQUE(article_id)
);
```

```sql
-- 推送成功后批量记录去重（INSERT OR IGNORE，幂等）
-- 注意：需在 feeds.db 连接下执行，或在 feeds.db 中通过 ATTACH 后使用 digest.pushed_articles
INSERT OR IGNORE INTO digest.pushed_articles (article_id, feed_id, pushed_at)
VALUES (?, ?, datetime('now'));
```

**说明**：
- digest.db 与 feeds.db 分属不同数据库，无外键约束
- 查询前需 `ATTACH digest.db AS digest`，写入时指定 `digest.pushed_articles`
- `UNIQUE(article_id)` + `INSERT OR IGNORE` 保证幂等，重复插入不报错
- 每次生成简报后批量插入该 feed 的所有 article_id

## 飞书推送

```bash
# 群组推送
openclaw message send \
  --channel feishu \
  --target "chat:oc_97c792a037da30fe0e1079e4b63f4bf7" \
  --message "简报内容"
```

**行为契约**：
- 格式：纯文本 Markdown（飞书群消息不支持卡片）
- 长度：≤800 字（Agent 负责截断）
- 频率：每源每日最多 1 条（去重保证）
- 错误：推送失败 → 不记录 pushed_articles，下次重试

## Cron 配置

```bash
# 每日 8:00 触发（一次性配置）
openclaw cron create \
  --agent RSS_article \
  --channel feishu \
  --to "chat:oc_97c792a037da30fe0e1079e4b63f4bf7" \
  --cron "0 8 * * *" \
  --timeout 300 \
  --prompt "执行每日 RSS 简报采集与推送"
```

## 手动触发

```bash
# 手动执行完整推送流程（与 Cron 触发逻辑完全相同）
openclaw agents run RSS_article
```

## 字数与格式

- 总字数 ≤ 800 字
- 每篇文章必有 1-2 句摘要 + 原文链接（不限文章数量）
- 无新文章：不推送
- 标题行格式：`📰 RSS 每日简报 — {订阅源名称}`
- 日期格式：`YYYY-MM-DD`（北京时间）

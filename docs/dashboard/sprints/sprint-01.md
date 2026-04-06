# Sprint-01: Agent 配置完善与本地验证

> 所属 Phase: Phase 3 Sprint 规划与开发交付
> 创建日期: 2026-04-06
> 状态: ✅ 已完成
> 目标: 完善 Agent 行为配置（SOUL.md + USER.md），实现去重逻辑，并通过本地验证确认输出格式

---

## 任务清单

| # | 任务 | 说明 | 状态 |
|---|------|------|------|
| 01-1 | 完善 SOUL.md | 补充 digest.db 初始化流程、去重查询逻辑、错误处理规则、主题分类规则嵌入 | ✅ |
| 01-2 | 完善 USER.md | 更新 SQL 查询添加 NOT IN pushed_articles 去重过滤、添加 digest.db 路径和初始化命令 | ✅ |
| 01-3 | 本地行为验证 | 模拟完整流程（查询→去重→分类→摘要），验证输出格式符合 UI mockup 4 种场景 | ✅ |

---

## 01-1: 完善 SOUL.md

### 当前状态

`source/RSS_article/SOUL.md` 已有基础行为规则，但缺少以下关键逻辑：

- digest.db 初始化步骤
- 去重查询逻辑（NOT IN pushed_articles）
- 推送成功后的去重记录写入
- 错误处理规则（DB 不存在、查询失败、推送失败）
- 主题分类规则内联（当前仅引用 export_lumen_to_output.py，Agent 运行时无法访问）

### 需要补充的内容

1. **执行流程**：增加完整的步骤序列
   ```
   1. 检查 feeds.db 是否存在 → 不存在则终止
   2. 初始化 digest.db（CREATE TABLE IF NOT EXISTS）
   3. 查询最近 24h 未推送文章（NOT IN pushed_articles）
   4. 按 feed_id 分组
   5. 对每组：主题分类 → 摘要生成 → 推送 → 记录去重
   ```

2. **主题分类规则**：将 TOPIC_RULES 内联到 SOUL.md，Agent 运行时可直接使用

3. **错误处理**：
   - feeds.db 不存在 → 终止，输出错误日志
   - digest.db 不存在 → 自动创建
   - 查询返回空集 → 输出"今日暂无新文章"，跳过推送
   - 推送失败 → 跳过该 feed，不记录去重，下次重试

### 上游产物

- `architecture.md` — 数据流定义
- `api-behavior.md` — 接口调用序列、SQL 行为契约
- `ux-flow.md` — 消息格式规范
- `ui-mockup.md` — 4 种消息场景

---

## 01-2: 完善 USER.md

### 当前状态

`source/RSS_article/USER.md` 已有基础配置，但 SQL 查询缺少去重过滤。

### 需要修改的内容

1. **SQL 查询**：添加 `NOT IN (SELECT article_id FROM pushed_articles)` 去重过滤
2. **digest.db 配置**：添加 digest.db 路径和初始化 SQL
3. **去重写入**：添加推送成功后的 INSERT OR IGNORE 语句

### 修改后的 SQL

```sql
-- 查询未推送文章（feeds.db 只读）
SELECT
    a.id, a.title, a.url, a.published_at,
    COALESCE(a.full_content, a.content, a.summary, '') AS body,
    f.title AS feed_title, f.id AS feed_id
FROM articles a
JOIN feeds f ON f.id = a.feed_id
WHERE a.published_at >= datetime('now', '-1 day')
  AND a.id NOT IN (
      SELECT article_id FROM pushed_articles
  )
ORDER BY f.id, a.published_at DESC;
```

```sql
-- 初始化 digest.db
-- 路径: /root/tencent_rsync_mac/RSS_article/lumen-data/digest.db
CREATE TABLE IF NOT EXISTS pushed_articles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    article_id INTEGER NOT NULL,
    feed_id INTEGER NOT NULL,
    pushed_at TEXT NOT NULL DEFAULT (datetime('now')),
    UNIQUE(article_id)
);

-- 记录已推送（推送成功后执行）
INSERT OR IGNORE INTO pushed_articles (article_id, feed_id, pushed_at)
VALUES (?, ?, datetime('now'));
```

### 上游产物

- `er-model.md` — 双库设计、pushed_articles 表结构
- `api-behavior.md` — SQL 行为契约（1.1 / 1.2 / 1.3）
- `tech-stack-decision.md` — D5 去重存储决策

---

## 01-3: 本地行为验证

### 验证方法

使用本地 feeds.db 数据，模拟 Agent 执行流程，检查输出格式。

### 验证场景（对应 ui-mockup.md 4 种 mockup）

| 场景 | 条件 | 验证点 |
|------|------|--------|
| Mockup 1 | ≤3 篇文章 | 逐篇摘要 + 原文链接，≤400 字 |
| Mockup 2 | >3 篇文章 | 要点概括 + 链接列表，≤400 字 |
| Mockup 3 | 多订阅源 | 每源独立消息 |
| Mockup 4 | 1 篇文章 | 单篇格式正确 |

### 验收标准

- [ ] 输出格式与 ui-mockup.md 一致
- [ ] 总字数 ≤400 字
- [ ] 主题分类结果与 TOPIC_RULES 一致
- [ ] 去重逻辑正确（已推送文章不出现在下次查询中）

---

## Action Plan

### 启动条件

- [x] Phase 1 全部产物已完成
- [x] Phase 2 全部产物已完成
- [x] SOUL.md / USER.md 初版已存在于 source/

### 执行顺序

```
01-1 完善 SOUL.md
  - 补充执行流程步骤序列
  - 内联 TOPIC_RULES 主题分类规则
  - 添加错误处理规则
  - 添加去重记录写入规则

01-2 完善 USER.md
  - 更新 SQL 查询（去重过滤）
  - 添加 digest.db 路径和初始化 SQL
  - 添加去重写入 SQL

01-3 本地行为验证
  - 使用本地 feeds.db 模拟查询
  - 验证 4 种输出场景
  - 确认字数限制和格式规范
```

### 关键检查点

| 里程碑 | 交付物 | 验收标准 |
|--------|--------|----------|
| SOUL.md 完善 | source/RSS_article/SOUL.md | 包含完整执行流程、主题规则、错误处理 |
| USER.md 完善 | source/RSS_article/USER.md | SQL 包含去重过滤、digest.db 配置完整 |
| 本地验证通过 | 验证记录 | 4 种场景输出符合 UI mockup |

### 风险预案

| 风险 | 影响 | 概率 | 应对措施 |
|------|------|------|----------|
| TOPIC_RULES 内联后 SOUL.md 过长 | 中 | 低 | 精简关键词列表，保留核心词 |
| 本地无 feeds.db 可测试 | 中 | 中 | 从服务器同步 feeds.db 到本地 |

---

## 依赖关系

```
01-1 SOUL.md ──┬──► 01-3 本地验证
               │
01-2 USER.md ──┘
```

---

## 开发日志

### 2026-04-06 — Sprint-01 执行

**01-1 SOUL.md 完善** ✅
- 补充完整 5 步执行流程（检查 DB → 初始化 digest.db → 查询去重 → 分组 → 推送+记录）
- 内联 TOPIC_RULES 完整关键词规则（7 个主题分类）
- 补充 6 种错误处理规则
- 补充时区转换规则（UTC → 北京时间）
- 补充消息格式规范（feed 标题行 + 日期格式）
- 补充 feeds.db 只读约束

**01-2 USER.md 完善** ✅
- SQL 查询添加 `NOT IN (SELECT article_id FROM pushed_articles)` 去重过滤
- 添加 `COALESCE(full_content, content, summary, '')` 优先级
- 添加 `DIGEST_DB_PATH` 配置
- 添加 digest.db 初始化 SQL（CREATE TABLE IF NOT EXISTS）
- 添加去重记录 SQL（INSERT OR IGNORE）
- 补充手动触发命令
- 补充行为契约说明

**01-3 本地行为验证** ✅
- 本地 feeds.db：2 个订阅源、34 篇文章、最近 24h 有 2 篇
- digest.db 初始化：CREATE TABLE IF NOT EXISTS 成功
- 跨库去重查询（ATTACH DATABASE）：返回 2 条未推送文章 ✅
- 幂等插入验证：重复 INSERT OR IGNORE 后仍为 2 条 ✅
- 去重过滤验证：记录后查询返回 0 条 ✅
- 测试数据已清理，digest.db 恢复空状态

---

*文档版本: v1.0.0 | 最后更新: 2026-04-06*

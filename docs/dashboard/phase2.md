# Phase 2 - 软件工程架构阶段

> 状态: 🟢 已完成
> 最后更新: 2026-04-06

## 阶段目标

- 形成 API、ER、UX 和技术架构方案

## 产物清单

| 产物 | 路径 | 状态 |
|------|------|------|
| API 行为设计 | [api-behavior.md](../specs/api-behavior.md) | 已完成 |
| ER 模型设计 | [er-model.md](../specs/er-model.md) | 已完成 |
| UX 交互流 | [ux-flow.md](../specs/ux-flow.md) | 已完成 |
| UI Mockup | [ui-mockup.md](../specs/ui-mockup.md) | 已完成 |
| 技术架构 | [architecture.md](../specs/architecture.md) | 已完成 |
| 技术决策 | [tech-stack-decision.md](../specs/tech-stack-decision.md) | 已完成 |

## 关键架构决策

1. **双数据库设计** — feeds.db（lumen 只读）+ digest.db（Agent 读写去重），职责隔离
2. **Agent 行为接口** — 通过 SQL 查询 + OpenClaw CLI 与外部交互，无传统 REST API
3. **消息格式** — 纯文本 Markdown，≤3 篇逐篇摘要，>3 篇要点+链接列表
4. **主题分类** — 复用 export_lumen_to_output.py 的 TOPIC_RULES 关键词匹配
5. **去重机制** — pushed_articles 表，UNIQUE(article_id) + INSERT OR IGNORE

## 门禁检查

| 条件 | 状态 |
|------|------|
| 数据模型（ER）已确认 | 通过 — feeds.db 只读 + digest.db 去重 |
| 接口行为（API）已定义 | 通过 — SQL 接口 + CLI 接口 + Agent 内部行为 |
| 交互流程（UX）已设计 | 通过 — Cron/手动触发 + 飞书消息格式 |
| 技术架构已收敛 | 通过 — 组件职责清晰，数据流明确 |
| 技术决策已记录 | 通过 — 8 项决策全部记录 |

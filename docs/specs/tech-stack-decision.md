# 技术决策

> 项目: RSS_article
> 状态: 已确认

## 决策清单

### D1: RSS 抓取工具 → lumen

| 项目 | 说明 |
|------|------|
| 选型 | [lumen](https://github.com/gilesknap/lumen)（Rust RSS 阅读器） |
| 理由 | 已有部署，成熟稳定，支持全文抓取，SQLite 存储 |
| 替代方案 | feedparser (Python)、rss2email |
| 决策时间 | 项目启动前已确定 |

### D2: 数据库 → SQLite

| 项目 | 说明 |
|------|------|
| 选型 | SQLite（WAL 模式） |
| 理由 | lumen 原生使用，无需额外部署；单机场景足够；WAL 模式支持并发读写 |
| 替代方案 | PostgreSQL（过度）、MySQL（过度） |
| 约束 | 仅支持单机部署，不支持分布式 |

### D3: AI Agent 框架 → OpenClaw

| 项目 | 说明 |
|------|------|
| 选型 | OpenClaw（Agent 平台） |
| 理由 | 已有部署，支持 Cron 调度、飞书集成、CLI 触发 |
| 替代方案 | LangChain + 自建调度、n8n、Dify |
| 决策时间 | 项目启动前已确定 |

### D4: 消息通道 → 飞书群组

| 项目 | 说明 |
|------|------|
| 选型 | 飞书群组消息（纯文本 Markdown） |
| 理由 | 用户日常工作在飞书，群消息无需额外操作即可查看 |
| 替代方案 | Telegram Bot、企业微信、邮件 |
| 约束 | 仅支持纯文本 Markdown，不支持富文本卡片 |

### D5: 去重存储 → 独立 SQLite 数据库

| 项目 | 说明 |
|------|------|
| 选型 | digest.db（独立于 feeds.db） |
| 理由 | 不修改 lumen 管理的 feeds.db，职责隔离；SQLite 零部署 |
| 替代方案 | JSON 文件（并发不安全）、写入 feeds.db 新表（侵入 lumen schema） |
| 决策理由 | 遵循"feeds.db 只读"原则，Agent 自管理去重数据 |

### D6: 主题分类 → 关键词规则匹配

| 项目 | 说明 |
|------|------|
| 选型 | TOPIC_RULES 关键词匹配（复用 export_lumen_to_output.py） |
| 理由 | 简单可控，结果可预测，与导出脚本保持一致 |
| 替代方案 | LLM 分类（延迟高、成本高、结果不稳定）、TF-IDF（过度） |
| 约束 | 新增主题需手动添加关键词规则 |

### D7: 摘要生成 → Agent 内置能力

| 项目 | 说明 |
|------|------|
| 选型 | OpenClaw Agent LLM 摘要（SOUL.md 规则驱动） |
| 理由 | 无需额外 API 调用，Agent 天然具备文本理解能力 |
| 替代方案 | 调用独立 LLM API（增加复杂度）、纯提取式摘要（质量低） |
| 约束 | 摘要质量依赖 LLM 能力，需通过 SOUL.md 持续优化 |

### D8: 文章导出脚本 → Python

| 项目 | 说明 |
|------|------|
| 选型 | Python 3 + 标准库 |
| 理由 | 已有实现（export_lumen_to_output.py），用于文章归档而非推送流程 |
| 替代方案 | Rust（与 lumen 同语言，但开发效率低） |
| 说明 | 导出脚本与推送 Agent 是独立的两条路径 |

## 决策摘要

| 编号 | 决策 | 类型 | 状态 |
|------|------|------|------|
| D1 | RSS 抓取 → lumen | 工具选型 | 已确定（前置） |
| D2 | 数据库 → SQLite (WAL) | 存储选型 | 已确定（前置） |
| D3 | Agent 框架 → OpenClaw | 平台选型 | 已确定（前置） |
| D4 | 消息通道 → 飞书群组 | 通道选型 | 已确定（前置） |
| D5 | 去重存储 → 独立 digest.db | 架构决策 | Phase 2 确定 |
| D6 | 主题分类 → 关键词规则 | 算法选型 | Phase 2 确定 |
| D7 | 摘要生成 → Agent LLM | 能力选型 | Phase 2 确定 |
| D8 | 导出脚本 → Python | 工具选型 | 已确定（前置） |

## 技术栈全景

```
┌─────────────────────────────────────────┐
│              RSS_article 技术栈          │
│                                         │
│  数据层:   SQLite (feeds.db + digest.db)│
│  抓取层:   lumen (Rust)                 │
│  Agent层:  OpenClaw (LLM)               │
│  推送层:   OpenClaw CLI → 飞书 API       │
│  调度层:   OpenClaw Cron                │
│  导出层:   Python 3 (独立脚本)           │
│  部署层:   腾讯云 Ubuntu 24.04           │
└─────────────────────────────────────────┘
```

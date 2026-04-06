# RSS_article

基于 lumen（Rust RSS 阅读器）抓取 RSS 订阅源，通过 OpenClaw Agent 每日自动聚合摘要，推送到飞书群组。

## 项目概述

- **类型**: 信息聚合与定时推送
- **技术栈**: Python + SQLite + OpenClaw + 飞书
- **部署环境**: 腾讯云 Ubuntu 24.04

## 核心流程

```
lumen fetch → feeds.db → OpenClaw Agent（每日 8:00 Cron）
  → 按主题分类 → 生成摘要（≤400字） → 飞书群组推送
```

## 目录结构

```
RSS_article/
├── .42cog/              # 认知敏捷法配置
│   ├── meta/            # 项目元信息
│   ├── real/            # 现实约束
│   ├── cog/             # 认知模型
│   └── work/            # 工作记录
├── .claude/             # Claude Code 配置
├── config/              # 飞书等配置（敏感信息）
├── docs/
│   ├── dashboard/       # PM 阶段追踪
│   ├── specs/           # 需求与设计规约
│   ├── reports/         # 测试与部署报告
│   └── template.md      # 简报格式模板
├── lumen/               # lumen RSS 阅读器
├── lumen-data/          # SQLite 数据库（feeds.db）
├── source/              # 源文件（不纳入版本控制）
│   └── RSS_article/     # Agent 配置（SOUL.md / USER.md）
├── export_lumen_to_output.py  # 文章导出脚本
└── run_rss_export.sh    # 导出脚本包装
```

## 当前订阅源

- 老布的AI知识库 (`https://www.laobu.com/feed.xml`)

## PM 阶段进度

| Phase | 名称 | 状态 |
|-------|------|------|
| Phase 1 | 设计思维阶段 | 已完成 |
| Phase 2 | 软件工程架构阶段 | 已完成 |
| Phase 3 | Sprint 规划与开发交付 | Sprint-01 已完成 |

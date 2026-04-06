# DDD 业务域模型

> 项目: RSS_article
> 状态: 已确认

## Bounded Context: 信息聚合与推送

本系统只有一个核心 Bounded Context，职责是从 RSS 数据源聚合信息并推送到消息通道。

### 核心领域对象

```
┌─────────────────────────────────────────────────┐
│                信息聚合与推送                       │
│                                                  │
│  ┌──────────┐     1:N     ┌──────────┐           │
│  │  Feed     │────────────▶│ Article  │           │
│  │ 订阅源    │             │ 文章      │           │
│  └──────────┘             └────┬─────┘           │
│                                │                 │
│                                │ 归属             │
│                                ▼                 │
│                          ┌──────────┐            │
│                          │  Topic   │            │
│                          │ 主题      │            │
│                          └────┬─────┘            │
│                               │                  │
│                               │ 聚合              │
│                               ▼                  │
│                          ┌──────────┐            │
│                          │  Digest  │            │
│                          │ 简报      │            │
│                          └────┬─────┘            │
│                               │                  │
│                               │ 推送              │
│                               ▼                  │
│                          ┌──────────┐            │
│                          │ Channel  │            │
│                          │ 推送通道   │            │
│                          └──────────┘            │
└─────────────────────────────────────────────────┘
```

### 实体定义

#### Feed（订阅源）

| 属性 | 类型 | 说明 |
|------|------|------|
| id | string | 唯一标识 |
| title | string | 订阅源名称 |
| url | string | RSS feed 地址 |

**业务规则**: 一个 Feed 产生多篇 Article（1:N）

#### Article（文章）

| 属性 | 类型 | 说明 |
|------|------|------|
| id | string | 文章 ID |
| title | string | 标题 |
| url | string | 原文链接 |
| published_at | datetime | 发布时间（UTC） |
| content | text | 摘要内容 |
| full_content | text | 全文内容 |
| feed_id | string | 所属订阅源 |
| topic | string | 推断的主题（运行时计算） |

**业务规则**:
- 一篇 Article 归属一个 Feed
- published_at 需从 UTC 转换为北京时间显示
- topic 通过关键词规则从 title/content 推断，非存储字段

#### Topic（主题）

| 值 | 关键词示例 |
|------|------|
| AI与智能体 | AI, Agent, LLM, GPT, 大模型, 智能体 |
| 开发与Web技术 | API, 框架, 前端, 后端, 开源, Python |
| 硬件与设备 | 芯片, GPU, 手机, 机器人, 硬件 |
| 影视与娱乐 | 电影, 音乐, 游戏, 动画 |
| 社区与活动 | 开源社区, 大会, 发布会, V2EX |
| 隐私与数字生活 | 隐私, 数据安全, 监控, 加密 |
| 商业与公司史 | 融资, 上市, 并购, 创业 |
| 未分类 | 不匹配以上规则 |

**业务规则**: 主题通过关键词匹配推断，一篇 Article 归属一个 Topic

#### Digest（简报）

| 属性 | 类型 | 说明 |
|------|------|------|
| date | date | 简报日期 |
| articles | list[Article] | 包含的文章列表 |
| format | enum | `detailed`（≤3篇）或 `summary`（>3篇） |
| content | text | 生成的简报文本 |
| total_chars | int | 总字数（≤400） |

**业务规则**:
- 一份 Digest 包含当日所有新文章
- format 由文章数量自动决定
- total_chars 硬限制 400，超出需压缩

#### Channel（推送通道）

| 属性 | 类型 | 说明 |
|------|------|------|
| type | enum | `feishu` |
| target | string | 群组 chat_id |
| policy | enum | `allowlist` |

**业务规则**: 当前仅支持飞书通道，allowlist 策略限制可访问群组

### 值对象

- **TimeWindow**: 24 小时查询窗口（`published_at >= now() - 1 day`）
- **CharLimit**: 400 字硬限制
- **Schedule**: 每日 8:00（Cron: `0 8 * * *`）
- **TriggerMode**: `cron`（自动）或 `manual`（手动）

### 去重机制

```
PushedArticle（已推送记录）
  ├── article_id: 文章 ID（联合唯一）
  ├── feed_id: 订阅源 ID
  ├── pushed_at: 推送时间
  └── UNIQUE(article_id)
```

**业务规则**:
- 每次推送成功后记录文章 ID
- 下次查询时过滤已推送的文章
- 去重记录可存储在独立表或文件中

### 领域事件

| 事件 | 触发条件 | 消费者 |
|------|---------|--------|
| ArticlesFetched | lumen 完成抓取写入 DB | Agent（读取） |
| DigestGenerated | Agent 完成摘要生成 | 推送服务 |
| DigestPushed | 消息成功发送到飞书 | 去重记录（写入） |
| NoNewArticles | 24h 内无新文章 | Agent（跳过推送） |
| ManualTrigger | 用户执行 openclaw agents run | Agent（执行推送流程） |

### 限界上下文间关系

```
[RSS 抓取上下文]          [信息聚合上下文]         [消息推送上下文]
  (lumen)                  (Agent)                (OpenClaw)
       │                         │                      │
       │ feeds.db               │                      │
       │────────────────────────▶│                      │
       │                         │ 简报文本              │
       │                         │─────────────────────▶│
       │                         │                      │ 飞书 API
       │                         │                      │──────────▶
```

**集成方式**: 通过共享数据库（feeds.db）和 CLI 命令（openclaw message send）实现上下文间通信，无直接 API 调用。

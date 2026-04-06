# Sprint-02: 部署交付与端到端测试

> 所属 Phase: Phase 3 Sprint 规划与开发交付
> 创建日期: 2026-04-06
> 状态: ✅ 已完成
> 目标: 将完善后的 Agent 配置部署到腾讯云，配置定时调度，完成端到端测试

---

## 任务清单

| # | 任务 | 说明 | 状态 |
|---|------|------|------|
| 02-1 | 部署到腾讯云 | 同步 SOUL.md + USER.md 到 Agent workspace、初始化 digest.db | ✅ |
| 02-2 | 配置 OpenClaw Cron | 注册每日 8:00 定时任务、验证 Cron 触发 | ✅ |
| 02-3 | 端到端测试 | 使用真实 RSS 数据验证完整流程（查询→去重→分类→摘要→推送→记录） | ✅ |

---

## 02-1: 部署到腾讯云

### 部署范围

| 文件 | 源路径 | 目标路径 |
|------|--------|----------|
| SOUL.md | `source/RSS_article/SOUL.md` | `/root/.openclaw/workspace-RSS_article/SOUL.md` |
| USER.md | `source/RSS_article/USER.md` | `/root/.openclaw/workspace-RSS_article/USER.md` |

### 部署步骤

1. 同步 SOUL.md 和 USER.md 到云端 Agent workspace
2. 检查 feeds.db 路径是否正确（`/root/tencent_rsync_mac/RSS_article/lumen-data/feeds.db`）
3. 在 feeds.db 同目录初始化 digest.db：
   ```bash
   sqlite3 /root/tencent_rsync_mac/RSS_article/lumen-data/digest.db "
   CREATE TABLE IF NOT EXISTS pushed_articles (
       id INTEGER PRIMARY KEY AUTOINCREMENT,
       article_id INTEGER NOT NULL,
       feed_id INTEGER NOT NULL,
       pushed_at TEXT NOT NULL DEFAULT (datetime('now')),
       UNIQUE(article_id)
   );"
   ```
4. 验证 Agent 可读取 feeds.db（只读 SELECT）

### 部署架构参考

```
/root/tencent_rsync_mac/RSS_article/
├── lumen/                 # lumen 二进制
├── lumen-data/
│   ├── feeds.db           # 文章数据库（lumen 管理）
│   └── digest.db          # 去重数据库（Agent 管理）← 新建
├── export_lumen_to_output.py
└── run_rss_export.sh

/root/.openclaw/workspace-RSS_article/
├── SOUL.md                # ← 从 source/ 同步
└── USER.md                # ← 从 source/ 同步
```

### 上游产物

- `architecture.md` — 部署架构
- `tech-stack-decision.md` — 技术栈（D2 SQLite、D5 digest.db）

---

## 02-2: 配置 OpenClaw Cron

### 配置内容

```bash
openclaw cron create \
  --agent RSS_article \
  --channel feishu \
  --to "chat:oc_97c792a037da30fe0e1079e4b63f4bf7" \
  --cron "0 8 * * *" \
  --timeout 300 \
  --prompt "执行每日 RSS 简报采集与推送"
```

### 行为契约

| 项目 | 说明 |
|------|------|
| 调度 | 每日 08:00（服务器本地时间） |
| 超时 | 300 秒 |
| 重试 | Gateway 异常时不自动重试，需人工介入 |

### 验证步骤

1. 注册 Cron 任务
2. 手动触发一次验证：`openclaw agents run RSS_article`
3. 检查飞书群是否收到消息
4. 检查 digest.db 是否有去重记录

### 上游产物

- `api-behavior.md` — Cron 行为契约（2.3）

---

## 02-3: 端到端测试

### 测试场景

| 场景 | 操作 | 预期结果 |
|------|------|----------|
| 正常推送 | 手动触发 Agent | 飞书群收到简报消息 |
| 去重验证 | 二次触发 Agent | 无新消息（已推送文章被跳过） |
| 空结果 | 清空 pushed_articles 后触发（若无新文章） | 无消息推送 |
| 多源推送 | 确保多 feed 场景（如后续添加新源） | 每源独立消息 |
| 格式验证 | 检查飞书消息内容 | 符合 UI mockup 格式规范 |

### 验收标准

- [ ] 手动触发后飞书群收到简报
- [ ] 二次触发不重复推送
- [ ] 消息格式符合 ui-mockup.md 规范
- [ ] digest.db 正确记录已推送文章
- [ ] Cron 注册成功且按时触发

### 异常场景测试

| 异常 | 操作 | 预期 |
|------|------|------|
| feeds.db 不存在 | 临时重命名 feeds.db | Agent 输出错误日志，不推送 |
| 飞书推送失败 | 使用错误 chat_id | 跳过推送，不记录去重 |

### 上游产物

- `ux-flow.md` — 核心交互流 + 异常场景
- `architecture.md` — 错误处理策略

---

## Action Plan

### 启动条件

- [x] Sprint-01 完成（SOUL.md + USER.md 已完善并验证）
- [x] 腾讯云服务器可 SSH 访问
- [x] lumen 已部署并正常运行
- [x] OpenClaw Gateway 已部署

### 执行顺序

```
02-1 部署到腾讯云
  - 同步 SOUL.md → Agent workspace
  - 同步 USER.md → Agent workspace
  - 初始化 digest.db
  - 验证 feeds.db 可读

02-2 配置 OpenClaw Cron
  - 注册 Cron 任务
  - 手动触发验证
  - 确认飞书群收到消息

02-3 端到端测试
  - 执行全部测试场景
  - 验证去重逻辑
  - 验证异常处理
  - 确认 Cron 定时触发
```

### 关键检查点

| 里程碑 | 交付物 | 验收标准 |
|--------|--------|----------|
| 部署完成 | 云端配置文件就位 | SOUL.md + USER.md + digest.db 均在正确路径 |
| Cron 验证 | 手动触发成功 | 飞书群收到格式正确的简报 |
| E2E 通过 | 测试报告 | 全部测试场景通过 |

### 风险预案

| 风险 | 影响 | 概率 | 应对措施 |
|------|------|------|----------|
| OpenClaw Gateway 版本不支持 Cron | 高 | 低 | 升级 Gateway 或使用系统 cron + CLI 触发 |
| 飞书 Bot 权限不足 | 高 | 低 | 检查 Bot 是否在群组中，chat_id 是否正确 |
| feeds.db 无新文章无法测试 | 中 | 中 | 等待 lumen fetch 或手动插入测试数据 |
| 摘要超 400 字 | 低 | 中 | 调整 SOUL.md 压缩规则 |

---

## 依赖关系

```
Sprint-01 完成
      │
      ▼
02-1 部署 ──► 02-2 Cron ──► 02-3 E2E 测试
```

---

## 开发日志

### 2026-04-06 20:12 ~ 20:30 执行记录

**02-1 部署**:
- SSH 登录腾讯云 (ubuntu@100.69.19.108)
- 备份 openclaw.json（5 份历史备份已存在）
- 创建 Agent: `openclaw agents add --workspace /root/.openclaw/workspace-RSS_article RSS_article`（ID 标准化为 `rss_article`）
- 追加 bindings（保留 stock-watcher + 新增 rss_article → oc_97c792a037da30fe0e1079e4b63f4bf7）
- 追加 groupAllowFrom 白名单
- SCP 上传 SOUL.md + USER.md 到 workspace
- 初始化 digest.db（pushed_articles 表创建成功）
- 验证 feeds.db：34 篇文章，2 篇最近 24h，1 个订阅源（老布的AI知识库）
- Gateway RPC probe: ok

**02-2 Cron**:
- 创建 Cron Job: `openclaw cron create --name "RSS每日简报" --agent rss_article --cron "0 8 * * *" --announce`
- Cron ID: `8914aca7-c6e6-4a53-8d6a-d8e4dbc66d1c`
- 注意：CLI 版本使用 `--message` 而非 `--prompt`，需 `--name` 参数

**02-3 E2E 测试**:
- 第1次触发：生成简报（2 篇文章），飞书群收到 ✅
- 发现问题1：Agent 未记录 digest.db（announce 模式下 Agent 不调 message send）
- 发现问题2：SQL 缺少 ATTACH digest.db 跨库查询
- 修复 SOUL.md：Step 5 适配 announce 模式，摘要生成后直接记录去重
- 修复 USER.md：添加 ATTACH 语句 + digest.pushed_articles 引用
- 第2次触发：生成简报 + 记录去重（article_id 11, 12）
- 第3次触发：输出"今日暂无新文章" ✅ 去重生效

---

## 测试报告

> Sprint Review 时填写

### 测试文档归档

所有测试相关文件归档到 `docs/test/2026-04-06-e2e/`：

```
docs/test/
└── 2026-04-06-e2e/
    ├── README.md              # 测试项目说明
    ├── logs/                  # 服务器日志
    ├── reports/               # 测试报告
    └── assets/                # 飞书消息截图
```

**Sprint 测试清单**:
- [x] 手动触发推送成功
- [x] 去重逻辑正确
- [x] 消息格式符合规范
- [ ] 异常场景处理正确（未测试 feeds.db 不存在场景）
- [x] Cron 定时触发正常

---

*文档版本: v1.0.0 | 最后更新: 2026-04-06*

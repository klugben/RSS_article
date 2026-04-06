---
name: Cloud_Openclaw_Quickstart
description: OpenClaw 云端部署与多渠道通知完整教程，供 AI 助手阅读使用。涵盖服务器连接、各通知渠道配置（微信/企业微信/飞书）、多 Agent 隔离与群组绑定、飞书 Bot 集成、Bitable 存储、Cron 定时推送、模型配置等。
---

# OpenClaw 云端部署与通知教程

## 0. 云端服务器

- **SSH**: `ssh -i /Users/ben/Qsync/My_Coding/GitHub/Key/mac_tencent_ecs_SP2026.pem ubuntu@100.69.19.108`
- **Tailscale IP**: 100.69.19.108
- **OS**: Ubuntu 24.04.4 LTS (kernel 6.8.0-101)
- **OpenClaw 安装目录**: `/root/.openclaw/`（root 用户下）
- **登录方式**: 先 `ssh ubuntu@100.69.19.108`，再 `sudo -i` 切换到 root
- **同步目录**: `/root/tencent_rsync_mac/`（Mac ↔ 云端双向同步）

## 1. 前置条件

- 云端已安装 `inotify-tools`、`notebooklm-py`、`jq`、`openclaw`
- Syncthing 已配置双向同步（Mac ↔ 云端 `input/`）
- OpenClaw 已配置企业微信和飞书通知渠道
- 飞书应用已创建并接入 OpenClaw（含 Bitable 读写权限）

---

## 2. 通知渠道配置速查

所有渠道共用同一个核心命令：

```bash
openclaw message send --channel <通道名> --target <接收方ID> --message "内容"
```

### 2.1 各渠道配置信息

| 渠道 | channel 值 | target 格式 | 已配置 ID |
|------|-----------|-------------|----------|
| 企业微信 Bot | `wecom` | Bot ID | `aibyLwMv-Aiqx8y1FHXH6XBjR-sIuDz6L7f` |
| 企业微信私聊 | `wecom` | `agent:main:wecom:direct:<用户名>` | `agent:main:wecom:direct:zhengxianben` |
| 企业微信群聊 | `wecom` | `agent:main:wecom:group:<群ID>` | `agent:main:wecom:group:wrfwlktaaa5qpnltfzznxgxjefnxcc4w` |
| 飞书 | `feishu` | `user:<open_id>` 或 `chat:<chat_id>` | 见 2.2 |
| 微信（大号） | `openclaw-weixin` | 微信 ID | `o9cq805YzYH_9f3UGeE8CzZb8S6w@im.wechat` |
| 微信（小号） | `openclaw-weixin` | 微信 ID | `o9cq8067UeEieLPS3X6mvd9IVc0Q@im.wechat` |

### 2.2 飞书 target 说明

| 场景 | target 格式 | 示例 |
|------|------------|------|
| 发给个人 | `user:<open_id>` | `user:ou_7ca0baab908771c828282c6229e767e1` |
| 发给群组 | `chat:<chat_id>` | `chat:oc_576beb66f7ce964242ecc0a3d674ec61` |

- **飞书 Bot App ID**: `cli_a94fbe2055785cce`
- **Stock Watcher 群组 chat_id**: `oc_576beb66f7ce964242ecc0a3d674ec61`

### 2.3 调用示例

```bash
# 确认 Gateway 运行状态
openclaw gateway status
openclaw gateway start    # 未启动时

# 飞书私聊
openclaw message send \
  --channel feishu \
  --target "user:ou_7ca0baab908771c828282c6229e767e1" \
  --message "任务完成"

# 飞书群组
openclaw message send \
  --channel feishu \
  --target "chat:oc_576beb66f7ce964242ecc0a3d674ec61" \
  --message "群组通知"

# 企业微信
openclaw message send \
  --channel wecom \
  --target "aibyLwMv-Aiqx8y1FHXH6XBjR-sIuDz6L7f" \
  --message "企业微信通知"

# 微信
openclaw message send \
  --channel openclaw-weixin \
  --target "o9cq805YzYH_9f3UGeE8CzZb8S6w@im.wechat" \
  --message "微信通知"

# 发送文件（所有渠道通用，路径必须绝对路径）
openclaw message send \
  --channel feishu \
  --target "chat:oc_576beb66f7ce964242ecc0a3d674ec61" \
  --message "报告已生成" \
  --media "/tmp/report.pdf"
```

### 2.4 在脚本中调用

```bash
#!/usr/bin/env bash
# 推荐封装为统一通知脚本: /usr/local/bin/notify.sh
set -euo pipefail
CHANNEL="${1:-feishu}"
TARGET="${2:-chat:oc_576beb66f7ce964242ecc0a3d674ec61}"
MSG="${3:-任务完成}"

openclaw message send --channel "$CHANNEL" --target "$TARGET" --message "$MSG"
```

```python
# Python 调用
import subprocess

subprocess.run([
    "openclaw", "message", "send",
    "--channel", "feishu",
    "--target", "chat:oc_576beb66f7ce964242ecc0a3d674ec61",
    "--message", "数据库备份完成"
], check=True)
```

```bash
# Crontab 定时通知
0 9 * * * /usr/bin/openclaw message send --channel feishu --target "chat:oc_576beb66f7ce964242ecc0a3d674ec61" --message "早上巡检完成"
```

---

## 3. Webhook 集成（外部进程 → OpenClaw）

适合：训练任务完成、爬虫批处理、服务异常报警、定时任务结果推送。

### 3.1 开启 hooks

在 `~/.openclaw/openclaw.json` 中配置：

```json
{
  "hooks": {
    "enabled": true,
    "token": "一个足够长的随机密钥",
    "path": "/hooks"
  }
}
```

配置后重启 Gateway：`openclaw gateway restart`

### 3.2 Webhook 端点

| 端点 | 用途 |
|------|------|
| `POST /hooks/agent` | 传递完整消息内容，OpenClaw 处理后转发 |
| `POST /hooks/wake` | 仅唤醒 Agent，由 Agent 自行读取文件/日志 |

### 3.3 hooks/agent 示例

```bash
curl -X POST http://127.0.0.1:18789/hooks/agent \
  -H 'Authorization: Bearer 你的hook密钥' \
  -H 'Content-Type: application/json' \
  -d '{
    "message": "请把下面内容原样简洁地通知给我：\n\n[任务完成]\njob_id=abc123\n耗时=42分钟\n结果=成功\n输出=/data/result.json",
    "name": "job-runner",
    "sessionKey": "job:abc123",
    "wakeMode": "now",
    "deliver": true,
    "channel": "last"
  }'
```

关键字段说明：

| 字段 | 说明 |
|------|------|
| `message` | 发给 Agent 的内容。建议明确写"请原样通知"，避免 Agent 自行发挥 |
| `name` | 来源名称标识 |
| `sessionKey` | 固定 key，方便串上下文 |
| `wakeMode` | `"now"` 立即处理 |
| `deliver` | `true` 让结果发出去 |
| `channel` | `"last"` 发回最近一次对话的渠道 |

### 3.4 hooks/wake 示例

```bash
curl -X POST http://127.0.0.1:18789/hooks/wake \
  -H 'Authorization: Bearer 你的hook密钥' \
  -H 'Content-Type: application/json' \
  -d '{"text":"转码任务完成，请检查结果文件","mode":"now"}'
```

适合结果在本地文件里、需要 Agent 进一步分析的场景。

### 3.5 openclaw agent CLI（替代 webhook）

```bash
openclaw agent --message "请通知我：备份完成，耗时 12 分钟，无错误。" --deliver
```

适合进程和 OpenClaw 在同一台机器、不想写 HTTP 调用的场景。

---

## 4. 多 Agent 隔离与飞书群组集成

> 本节整合 OpenClaw 多 Agent 配置方法与 Stock Watcher 项目实战经验。
> 单个 Agent 处理多类任务会带来严重的记忆负担，极大程度拉高 Token 消耗。
> OpenClaw 支持创建多个相互隔离的 Agent，分别具有不同的人格、技能、记忆、工作空间，实现"AI 军团"协作。

### 4.0 核心机制

- **Agent 是隔离的"脑"**：拥有独立 workspace（记忆、技能等均在 workspace 中）、独立 sessions
- **路由到哪个 Agent**：由配置里的 `bindings` 决定（最具体规则优先）
- **每个 Agent 用哪个模型**：可在 `agents.list[].model` 单独配置；运行时会优先用该 Agent 的 model 覆盖默认值
- **方案设计**：默认主 Agent 处理全部私聊，每个群绑定到不同的群组 Agent，记忆/技能/模型均可完全隔离

### 4.1 架构总览

```
本地 Mac (配置管理)                    云端 Ubuntu (OpenClaw Gateway :34606)
┌─────────────────────┐               ┌─────────────────────────────────────┐
│ config/feishu.env  │──rsync同步──▶│  Agent: stock-watcher (独立隔离)    │
│ source/stock-watcher/│              │  ├── Workspace:                    │
│   ├── SOUL.md       │              │  │  /root/.openclaw/                │
│   └── USER.md       │              │  │  workspace-stock-watcher/        │
└─────────────────────┘              │  ├── SOUL.md (Agent 人格+行为)     │
                                     │  ├── USER.md (运行时配置)          │
                                     │  ├── feishu_bitable skill (存储)   │
                                     │  └── agent-browser skill (采集)    │
                                     │                                     │
                                     │  Cron Jobs (7个, 工作日自动执行)    │
                                     │  └── announce 模式 → 飞书群组 Bot   │
                                     └──────────┬──────────────────────────┘
                                                │
                                     ┌──────────▼──────────────────────────┐
                                     │ 飞书                                 │
                                     │  ├── 群组 Bot 推送 (announce)        │
                                     │  ├── 多维表格 Bitable (数据存储)     │
                                     │  └── 关键词触发 (@Bot 股指监控)      │
                                     └─────────────────────────────────────┘
```

**核心特点**：无服务器函数、无前端、无数据库 — 全部依赖 OpenClaw Agent + 飞书生态。

### 4.2 feishu.env 配置文件

路径：`config/feishu.env`，修改后需同步到服务器并 `openclaw gateway restart`。

```bash
# ============================================
# Stock Watcher 配置文件
# 修改后需同步到服务器并重启 Gateway 生效
# 服务器: sudo -i && openclaw gateway restart
# ============================================

# --- 飞书多维表格 ---
# 空间: Stock_watcher_lark
# 获取方式:
#   1. 打开飞书 → 进入多维表格文档
#   2. 浏览器地址栏 URL 格式: https://xxx.feishu.cn/base/{BASE_TOKEN}
#      → BASE_TOKEN 即为 App Token
#   3. 各 table_id 获取: 打开多维表格 → 点击对应数据表 → URL 中 tblXXXXXX 部分
#
FEISHU_BASE_TOKEN=BuNEbKgTrapQnFs0wu5cJRRknXe
FEISHU_TABLE_MARKET_DATA=tblh4exA56AgJQ06
FEISHU_TABLE_STRATEGY_CONFIG=tblTpjdRYRSbPPSa
FEISHU_TABLE_FETCH_LOG=tblX53Lsy06WQD7c

# --- OpenClaw Agent ---
# 获取方式:
#   服务器上执行 `openclaw agents list` 查看所有 Agent
#   创建新 Agent: `openclaw agents add --workspace <路径> <agent-id>`
#
OPENCLAW_AGENT_ID=stock-watcher
OPENCLAW_AGENT_WORKSPACE=/root/.openclaw/workspace-stock-watcher

# --- 飞书群组绑定 ---
# chat_id 获取方式:
#   1. 打开飞书群组 → 右上角 ... → 设置 → 拉到最底部
#   2. 找到"群组信息" → 点击"复制"按钮
#   3. 得到的格式为 oc_xxxxxxx（去掉 "chat:" 前缀后填入）
#
# 群组策略说明:
#   allowlist = 仅允许下面 groupAllowFrom 列出的群组访问
#   open = 允许所有群组（不推荐）
#
FEISHU_GROUP_CHAT_ID=oc_576beb66f7ce964242ecc0a3d674ec61
FEISHU_GROUP_POLICY=allowlist
```

| 配置项 | 说明 | 获取方式 |
|--------|------|----------|
| `FEISHU_BASE_TOKEN` | 多维表格 App Token | 飞书多维表格 URL 中 `base/` 后面部分 |
| `FEISHU_TABLE_*` | 各数据表 table_id | 多维表格内各表 URL 中 `tblXXXXXX` |
| `OPENCLAW_AGENT_ID` | Agent 标识 | `openclaw agents list` |
| `OPENCLAW_AGENT_WORKSPACE` | Agent 独立工作空间 | 创建 Agent 时 `--workspace` 指定 |
| `FEISHU_GROUP_CHAT_ID` | 群组会话 ID | 群设置 → 最底部 → 复制 |
| `FEISHU_GROUP_POLICY` | 群组访问策略 | `allowlist`(白名单) 或 `open` |

### 4.3 服务器端配置步骤

#### 步骤 1：备份配置文件

在对配置文件进行修改前，强烈建议先备份：

```bash
cp ~/.openclaw/openclaw.json ~/.openclaw/openclaw.json.backup.$(date +%Y%m%d_%H%M%S)
ls -la ~/.openclaw/openclaw.json*
```

> **恢复方法**：如果后续配置过程中 OpenClaw 启动失败或行为异常：
> ```bash
> cp ~/.openclaw/openclaw.json.backup.YYYYMMDD_HHMMSS ~/.openclaw/openclaw.json
> openclaw gateway restart
> ```

#### 步骤 2：创建独立 Agent

```bash
sudo -i
openclaw agents add --workspace /root/.openclaw/workspace-stock-watcher stock-watcher
openclaw agents list   # 确认创建成功
```

**参数说明**：

| 参数 | 说明 |
|------|------|
| `--workspace` | 指定独立的数据空间路径，建议格式：`/root/.openclaw/workspace-<agent-id>` |
| `<agent-id>` | 推荐格式：`feishu-<团队名>-<用途>` 或 `<项目名>` |
| `--model` | 可选，指定自定义模型 ID，否则使用默认模型 |

#### 步骤 3：配置飞书群组绑定

> **严重警告**：`openclaw config set --json bindings` 会**整体替换**当前配置！
> 如果已有其他 bindings（QQ、Telegram 等），**必须先备份**：
> ```bash
> openclaw config get bindings > /tmp/bindings-backup.json
> ```
> 然后在原有数组基础上**追加**新绑定，再整体写回去。

```bash
# 如果有已有绑定，先读取再追加；如果是全新配置，直接执行：
openclaw config set --json bindings '[
  {
    "agentId": "stock-watcher",
    "match": {
      "channel": "feishu",
      "peer": {
        "kind": "group",
        "id": "oc_576beb66f7ce964242ecc0a3d674ec61"
      }
    }
  }
]'
```

#### 步骤 4：配置群组白名单

```bash
openclaw config set channels.feishu.groupPolicy allowlist
openclaw config set --json channels.feishu.groupAllowFrom '["oc_576beb66f7ce964242ecc0a3d674ec61"]'
```

> 使用 `allowlist` 策略可确保只有配置在 `groupAllowFrom` 中的群组才能访问 OpenClaw，是一个安全措施。

#### 步骤 5：部署 Agent 配置文件

将 `SOUL.md` 和 `USER.md` 复制到 Agent 工作空间：

```bash
scp source/stock-watcher/SOUL.md root@100.69.19.108:/root/.openclaw/workspace-stock-watcher/
scp source/stock-watcher/USER.md root@100.69.19.108:/root/.openclaw/workspace-stock-watcher/
```

- **SOUL.md** — Agent 身份、行为规则、预警逻辑、推送格式
- **USER.md** — 运行时配置，包含飞书 Bitable token/table_id、关键词触发规则、采集流程

#### 步骤 6：添加 Bot 到飞书群组

飞书群组 → 右上角 `...` → 设置 → 群机器人 → 选择 Bot 应用添加。群组中 @Bot 即可触发 Agent。

> **注意**：此处添加的机器人和私聊的是同一个。默认情况下，群组内和机器人互动需要 @ 它。

#### 步骤 7：重启 Gateway

```bash
openclaw gateway restart
openclaw gateway status   # 确认 running
```

> 状态显示 `running` 即表示配置文件格式正确且加载成功。

### 4.4 验证 Agent 隔离效果

#### 测试 1：群组消息使用独立 Agent

在飞书群组中向机器人提问：`你所在的工作空间路径是什么？`

预期返回：`/root/.openclaw/workspace-stock-watcher`

#### 测试 2：主 Agent 与独立 Agent 隔离

与机器人进行 1 对 1 私聊，提问：`你所在的工作空间路径是什么？`

预期返回：`/root/.openclaw/workspace`（默认 workspace）

#### 测试 3：数据隔离验证

1. 在群组中让机器人记住某个信息：`记住：我们团队的代号是"北极星"`
2. 在私聊中询问：`你记得我们团队的代号是什么吗？`
3. 验证主 Agent 是否无法获取群组中的信息（应回答"不知道"）

#### 测试 4：bindings 配置确认

```bash
openclaw agents list --bindings
```

确认：
- `agentId` 是否与 `openclaw agents list` 中看到的 Agent ID 匹配
- `peer.id` 是否为正确的群组会话 ID

### 4.5 消息推送三种方式

#### 方式 1：Cron 定时推送（announce 模式，最常用）

Cron 触发 Agent 执行任务，Agent 输出自动推送到绑定的飞书群组。无需手动调用 `message send`。

```bash
# 创建 Cron Job
openclaw cron create \
  --agent stock-watcher \
  --channel feishu \
  --to "chat:oc_576beb66f7ce964242ecc0a3d674ec61" \
  --cron "15 9 * * 1-5" \
  --timeout 480 \
  --prompt "执行盘前简报采集与推送"

# 管理 Cron
openclaw cron list                              # 查看所有
openclaw cron run <cron-id>                     # 手动触发
openclaw cron edit --agent stock-watcher <id>   # 迁移到新 Agent
openclaw cron edit --channel feishu --to "chat:oc_xxx" <id>  # 改投递目标
```

**announce 模式原理**：Cron 触发 → Agent 执行 prompt → 生成回复 → OpenClaw 自动推送到 `--to` 指定的群组。

#### 方式 2：群组关键词触发

在飞书群组中 @Bot 发送关键词（如"股指监控"），OpenClaw 路由到绑定的 Agent，Agent 处理后在群组内回复。关键词在 SOUL.md / USER.md 中定义。

#### 方式 3：CLI 直接发消息（临时/调试）

```bash
openclaw message send --channel feishu --target "chat:oc_576beb66f7ce964242ecc0a3d674ec61" --message "手动通知"
```

### 4.6 飞书多维表格 (Bitable) 数据存储

Agent 通过 `feishu_bitable` skill 读写多维表格，实现无数据库持久化。

**前置权限**（飞书开放平台为应用开通）：
- `bitable:record:read`
- `bitable:record:write`

**三表结构**：

| 表名 | table_id | 用途 | 字段数 |
|------|----------|------|--------|
| market_data | `tblh4exA56AgJQ06` | 行情主表（价格+贴水+价差+预警+食利评分） | 43 |
| strategy_config | `tblTpjdRYRSbPPSa` | 策略参数配置（预警阈值、数据源权重等，19 行预置） | 8 |
| fetch_log | `tblX53Lsy06WQD7c` | 采集日志（数据源、耗时、状态） | 10 |

**写入方式**：在 USER.md 中配置参数后，Agent 自动通过 `feishu_bitable` skill 调用。幂等规则：同日期+时段使用 UPDATE 而非 CREATE。

### 4.7 静默模式与分级推送

Agent 根据时段和预警级别决定是否推送群组消息：

| 时段 | Cron | 策略 | 说明 |
|------|------|------|------|
| 盘前 | `15 9 * * 1-5` | 推送 | 飞书群组 + Bitable |
| 盘中 | `30 10 * * 1-5` | 推送 | 飞书群组 + Bitable |
| 盘中 | `0 11 * * 1-5` | 静默 | 仅 Bitable，预警≥WARNING 才推送 |
| 盘中 | `30 13 * * 1-5` | 静默 | 仅 Bitable，预警≥WARNING 才推送 |
| 盘中 | `0 14 * * 1-5` | 推送 | 飞书群组 + Bitable |
| 盘中 | `30 14 * * 1-5` | 静默 | 仅 Bitable，预警≥WARNING 才推送 |
| 盘后 | `15 15 * * 1-5` | 推送 | 飞书群组 + Bitable（完整日报） |

实现方式：Cron prompt 中指示当前时段策略，Agent 根据 SOUL.md 规则决定是否推送。

### 4.8 进阶操作

#### 为 Agent 配置自定义模型

```bash
openclaw agents add --workspace /root/.openclaw/workspace-feishu-writer --model kitcoding-openai/z-ai/glm4.7 feishu-writer
```

#### 为多个群组配置不同 Agent

重复上述步骤，在 `bindings` 中添加多个群组绑定：

```bash
openclaw config set --json bindings '[
  {
    "agentId": "feishu-writer",
    "match": {
      "channel": "feishu",
      "peer": {
        "kind": "group",
        "id": "oc_e4dfb35658c81ce5100add124c3592a8"
      }
    }
  },
  {
    "agentId": "feishu-operations",
    "match": {
      "channel": "feishu",
      "peer": {
        "kind": "group",
        "id": "oc_9f23c45769d92df621Bee02350c4603d"
      }
    }
  }
]'

openclaw config set --json channels.feishu.groupAllowFrom '[
  "oc_e4dfb35658c81ce5100add124c3592a8",
  "oc_9f23c45769d92df621Bee02350c4603d"
]'
```

#### 删除 Agent

```bash
openclaw agents delete feishu-writer
```

此命令会删除 Agent 的配置以及相关的 workspace 和 state 数据。

### 4.9 新建项目复用清单

按以下顺序操作，快速搭建新的"OpenClaw Agent + 飞书群组"项目：

**飞书侧**：
1. 创建飞书应用，开通消息推送 + Bitable 读写权限
2. 创建飞书群组，添加 Bot 到群组
3. 创建多维表格，获取 Base Token 和各 Table ID
4. 复制群组 chat_id（群设置 → 最底部 → 复制）

**本地配置**：
1. 创建 `config/feishu.env`，填入所有 ID 和 Token
2. 编写 `source/<agent-name>/SOUL.md`（Agent 人格 + 行为规则）
3. 编写 `source/<agent-name>/USER.md`（运行时配置，引用 feishu.env 中的值）

**服务器部署**：
1. `openclaw agents add --workspace /root/.openclaw/workspace-<name> <agent-id>`
2. 配置 `bindings`（**先备份已有配置！**）
3. 配置 `groupPolicy` + `groupAllowFrom`
4. 部署 SOUL.md 和 USER.md 到 workspace
5. `openclaw gateway restart`

**Cron 配置**：
1. 创建 Cron Job，指定 `--agent`、`--channel feishu`、`--to "chat:<id>"`
2. `openclaw cron run <id>` 手动测试

**验证**：
1. 群组 @Bot 发关键词，确认 Agent 响应
2. 检查 Bitable 是否有数据写入
3. `openclaw logs --follow` 查看运行日志

---

## 5. 模型配置（Codex OAuth + Fallback）

> 配置日期: 2026-03-28 | OpenClaw 版本: 2026.3.11

### 5.1 OAuth 登录 Codex

```bash
sudo -i
openclaw models auth login --provider openai-codex
```

云端无浏览器，需手动处理 OAuth 回调：
1. 复制命令输出的授权 URL → 在本地浏览器打开
2. 完成 OpenAI 登录授权
3. 浏览器重定向后，复制完整重定向 URL（`http://127.0.0.1:1455/auth/callback?code=...&state=...`）
4. 粘贴回云端终端完成认证

验证：`openclaw models status`，应显示 `openai-codex:default ok expires in 10d`

### 5.2 配置主模型和备用模型

```bash
openclaw models set openai-codex/gpt-5.4              # 主模型
openclaw models fallbacks add glmcode/GLM-5-Turbo     # 备用模型
```

故障转移：Codex 出错（超限、网络）→ 自动切换 GLM-5-Turbo。

### 5.3 模型管理命令

```bash
openclaw models status          # 查看当前配置
openclaw models list --all      # 所有可用模型
openclaw models auth login --provider openai-codex  # 重新登录
```

注意事项：
- OAuth token 约 10 天过期，OpenClaw 自动刷新，失败需重新登录
- OAuth 使用 `127.0.0.1:1455` 端口，仅本地访问
- 支持 ChatGPT Plus/Pro 订阅

---

## 6. 常用管理命令速查

```bash
# Gateway 管理
openclaw gateway status          # 查看状态
openclaw gateway start           # 启动
openclaw gateway restart         # 重启（修改配置后必须执行）

# Agent 管理
openclaw agents list             # 列出所有 Agent
openclaw agents list --bindings  # 查看绑定关系
openclaw agents add --workspace <路径> <agent-id>  # 创建 Agent
openclaw agents delete <agent-id>                  # 删除 Agent

# Cron 管理
openclaw cron list               # 列出所有 Cron
openclaw cron run <cron-id>      # 手动触发
openclaw cron create ...         # 创建（见 4.5）
openclaw cron edit ...           # 编辑

# 日志与诊断
openclaw logs --follow           # 实时日志
openclaw doctor                  # 诊断问题
openclaw doctor --repair         # 自动修复（如 systemd Node 路径）

# 配置管理
openclaw config get <key>        # 读取配置
openclaw config set <key> <val>  # 写入配置
openclaw config set --json <key> '<json>'  # 写入 JSON 配置
cp ~/.openclaw/openclaw.json ~/.openclaw/openclaw.json.backup.$(date +%Y%m%d_%H%M%S)  # 备份
```

---

## 7. 故障排查

| 问题 | 排查方法 |
|------|----------|
| Gateway 启动失败 | `cat ~/.openclaw/openclaw.json \| python3 -m json.tool` 检查 JSON 格式；恢复备份 |
| 群组 Bot 无响应 | `openclaw logs --follow`；检查 chat_id 是否在 `groupAllowFrom`；确认 Bot 已加入群组 |
| Agent 未起到隔离作用 | `openclaw agents list --bindings` 确认 `agentId` 与 `peer.id` 是否匹配 |
| Bitable 写入 403 | 飞书开放平台检查是否开通 `bitable:record:write` 权限 |
| Cron 不触发 | `openclaw cron list` 确认存在；检查 cron 表达式（工作日用 `1-5`） |
| Agent 响应错乱 | `openclaw agents list --bindings` 确认绑定关系 |
| 配置修改不生效 | 必须执行 `openclaw gateway restart` |
| OAuth token 过期 | `openclaw models auth login --provider openai-codex` 重新登录 |
| systemd Node 路径异常 | `openclaw doctor --repair` 自动修复 |
| 配置命令 JSON 格式错误 | 确保字符串使用双引号，数组最后一个元素后不要有逗号 |

### 常见问题

| 问题 | 回答 |
|------|------|
| 能否为一个群组配置多个 Agent？ | 不支持。每个群组只能绑定一个 Agent，但可为多个不同群组配置不同 Agent |
| 独立 Agent 是否继承主 Agent 的配置？ | 不继承。拥有完全独立的 workspace、记忆和状态，但可继承 `agents.defaults` 中的默认配置 |
| 能否将 Agent 切换到另一个群组？ | 可以。修改 `bindings` 中的 `peer.id` 为新会话 ID，更新 `groupAllowFrom` 并重启 Gateway。原群组数据不会自动迁移 |
| 命令行配置 vs 手动编辑配置文件？ | 推荐使用 `openclaw agents add` 和 `openclaw config set` 命令，比手动编辑更安全，会自动处理格式 |

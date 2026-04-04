---
name: Cloud_Openclaw_Quickstart
description: 提供从mac端登录腾讯云云服务器ubuntu系统,控制服务器上openclaw的方法,并由claude根据项目需要,补全后续管理方法,以便复用.
---


## 云端服务器
- **SSH**: `ssh -i /Users/ben/Qsync/My_Coding/GitHub/Key/mac_tencent_ecs_SP2026.pem ubuntu@100.69.19.108`
- **Tailscale IP**: 100.69.19.108
- **OS**: Ubuntu 24.04.4 LTS (kernel 6.8.0-101)


## 前置条件

- 云端 Ubuntu 服务器已安装 `inotify-tools`、`notebooklm-py`、`jq`、`openclaw`
- Syncthing 已配置双向同步（Mac ↔ 云端 `input/`）
- OpenClaw 已配置企业微信和飞书通知渠道,安装目录在root用户帐户下,/root/.openclaw/,可以先登录ubuntu帐户,再通过 sudo -i  转到root用户权限
- /root/tencent_rsync_mac/是云服务和本地mac的同步总目录,当前项目文件夹在/root/tencent_rsync_mac/本项目;



# 如何在ubuntu上调用openclaw channel通知用户
## 配置信息
- 企业微信bot:ID:aibyLwMv-Aiqx8y1FHXH6XBjR-sIuDz6L7f
- 企业微信私聊: agent:main:wecom:direct:zhengxianben (用户: zhengxianben)
-企业微信群聊: agent:main:wecom:group:wrfwlktaaa5qpnltfzznxgxjefnxcc4w
- 飞书bot:id:cli_a94fbe2055785cce
- 微信小号的bot:o9cq8067UeEieLPS3X6mvd9IVc0Q@im.wechat
- 微信大号:o9cq805YzYH_9f3UGeE8CzZb8S6w@im.wechat

## 微信配置方法

~~~
核心命令是：

openclaw message send --channel <通道名> --target <接收方ID> --message "你的结果"

1）先确认 OpenClaw 网关是活的
在云服务器上跑：

openclaw gateway status

如果没起来：

openclaw gateway start

2）让进程在结束时调用 message send

如果你要走企业微信通道
通道一般会是 wecom，写法类似：

openclaw message send \
--channel wecom \
--target "<你的企业微信接收ID>" \
--message "任务完成：foo 已处理完，结果是 bar"

如果你要走当前这个微信通道
你现在这个会话的通道是 openclaw-weixin。
当前聊天 ID 看起来是：

o9cq805YzYH_9f3UGeE8CzZb8S6w@im.wechat

那命令会像这样：

openclaw message send \
--channel openclaw-weixin \
--target "o9cq805YzYH_9f3UGeE8CzZb8S6w@im.wechat" \
--message "任务完成：脚本执行成功"

3）在你的程序里直接调用

Bash
RESULT="$(python3 /opt/job/run.py 2>&1)"
openclaw message send \
--channel openclaw-weixin \
--target "o9cq805YzYH_9f3UGeE8CzZb8S6w@im.wechat" \
--message "任务完成\n\n$RESULT"

Python
import subprocess

result = "任务完成，产出 123 条记录"

subprocess.run([
"openclaw", "message", "send",
"--channel", "openclaw-weixin",
"--target", "o9cq805YzYH_9f3UGeE8CzZb8S6w@im.wechat",
"--message", result
], check=True)

4）如果要发文件
OpenClaw 也可以发附件，重点是 本地路径必须用绝对路径：

openclaw message send \
--channel openclaw-weixin \
--target "o9cq805YzYH_9f3UGeE8CzZb8S6w@im.wechat" \
--message "报告已生成" \
--media "/tmp/report.pdf"

5）建议你这样封装
给服务器上做一个统一通知脚本，比如 /usr/local/bin/notify-me.sh：

#!/usr/bin/env bash
set -euo pipefail

MSG="${1:-任务完成}"
openclaw message send \
--channel openclaw-weixin \
--target "o9cq805YzYH_9f3UGeE8CzZb8S6w@im.wechat" \
--message "$MSG"

以后任何进程结束后只要：

notify-me.sh "转码完成：video_01.mp4"
~~~


## 企业微信

~~~
方案 1：外部进程 → OpenClaw webhook → 微信反馈
适合：
 ⦁训练任务完成
 ⦁爬虫/批处理跑完
 ⦁服务异常报警
 ⦁定时任务结果推送
1）先在 OpenClaw 配置里开启 hooks
大意像这样：
{
  hooks: {
    enabled: true,
    token: "一个足够长的随机密钥",
    path: "/hooks"
  }
}
然后重启 Gateway。

2）让你的服务器进程 POST 到  ⁠/hooks/agent⁠ 
例如：
curl -X POST http://127.0.0.1:18789/hooks/agent \
  -H 'Authorization: Bearer 你的hook密钥' \
  -H 'Content-Type: application/json' \
  -d '{
    "message": "任务完成：视频转码成功，共处理 18 个文件，输出目录 /data/out",
    "name": "transcode-job",
    "sessionKey": "job:transcode:daily",
    "wakeMode": "now",

"deliver": true,
    "channel": "last"
  }'
这几个字段最关键
 ⦁ ⁠message⁠ ：你想让我处理/转述的内容
 ⦁ ⁠name⁠ ：这个来源的名字
 ⦁ ⁠sessionKey⁠ ：给同一类任务一个固定 key，方便串上下文
 ⦁ ⁠deliver: true⁠ ：让结果发出去
 ⦁ ⁠channel: "last"⁠ ：发回最近一次对话的渠道

最推荐的 message 写法
如果你只是想“原样通知我”，建议直接把你想发的内容写清楚：

{
  "message": "请把下面内容原样简洁地通知给我：\n\n[任务完成]\njob_id=abc123\n耗时=42分钟\n结果=成功\n输出=/data/result.json",
  "name": "job-runner",

"sessionKey": "job:abc123",
  "wakeMode": "now",
  "deliver": true,
  "channel": "last"
}
这样 OpenClaw 会更稳定地把结果发出来，而不是“自己发挥过多”。

方案 2：直接用  ⁠openclaw agent⁠ 
如果你的进程运行环境里能直接调用  ⁠openclaw⁠  CLI，也可以这么干：

openclaw agent --message "请通知我：备份完成，耗时 12 分钟，无错误。" --deliver
这个方式适合：
 ⦁进程和 OpenClaw 在同一台机器
 ⦁你不想自己写 HTTP 调用
但从自动化角度讲，webhook 更通用、更好集成。

方案 3：只做事件唤醒，不传完整内容
如果你想让外部系统只发一个“有结果了”，再由我去读取文件、日志、数据库，也可以用：

curl -X POST http://127.0.0.1:18789/hooks/wake \
  -H 'Authorization: Bearer 你的hook密钥' \
  -H 'Content-Type: application/json' \

-d '{"text":"转码任务完成，请检查结果文件","mode":"now"}'
这个更适合：
 ⦁结果在本地文件里
 ⦁需要我进一步分析日志/生成摘要

~~~


## 飞书
~~~
我建议你的实际做法

A. shell 脚本里直接调用

_#!/usr/bin/env bash_

MSG="$1"

openclaw message send \

--channel feishu \

--target "user:ou_7ca0baab908771c828282c6229e767e1" \

--message "$MSG"

  
调用：

./notify.sh "任务执行成功"

B. Python 里调用

import subprocess

msg = "数据库备份完成"

subprocess.run([

"openclaw", "message", "send",

"--channel", "feishu",

"--target", "user:ou_7ca0baab908771c828282c6229e767e1",

"--message", msg

], check=True)

C. systemd / cron / CI 里调用

比如 crontab：

0 9 * * * /usr/bin/openclaw message send --channel feishu --target "user:ou_7ca0baab908771c828282c6229e767e1" --message "早上巡检完成"

  
比如部署脚本：

if ./deploy.sh; then

openclaw message send --channel feishu --target "user:ou_7ca0baab908771c828282c6229e767e1" --message "部署成功"

else

openclaw message send --channel feishu --target "user:ou_7ca0baab908771c828282c6229e767e1" --message "部署失败"

fi

目标地址怎么填

在你这个 Feishu 环境里，通常这样填：  

- 发给个人：user:<open_id>
    

- 发给群：chat:<chat_id>
    

你这次私聊上下文里，你本人就是：

user:ou_7ca0baab908771c828282c6229e767e1

  
所以外部进程要通知你，直接用这个 target 就行。
~~~







# 云端 OpenClaw 配置 Codex OAuth 及模型优先级

> 配置日期: 2026-03-28
> 服务器: Ubuntu 云服务器
> OpenClaw 版本: 2026.3.11

## 一、背景

在云端部署 OpenClaw 后，需要通过 OAuth 登录 OpenAI Codex（使用 ChatGPT 订阅），并配置模型优先级，实现主模型失败时自动切换到备用模型。

## 二、OAuth 登录 Codex

先在腾讯云登录root用户,点击OrcaTerm登录.

### 2.1 执行登录命令

```bash
openclaw models auth login --provider openai-codex
```

### 2.2 处理浏览器回调（关键步骤）

由于云端服务器无法打开本地浏览器，需要手动处理 OAuth 回调：

1. **复制命令输出的授权 URL**
   ```
   https://auth.openai.com/oauth/authorize?client_id=...&redirect_uri=http://127.0.0.1:1455/auth/callback&...
   ```

2. **在本地浏览器中打开该 URL**

3. **完成 OpenAI 登录授权**

4. **浏览器重定向后，复制完整的重定向 URL**
   ```
   http://127.0.0.1:1455/auth/callback?code=abc123&state=xyz
   ```

5. **粘贴回云端终端完成认证**

### 2.3 验证登录状态

```bash
openclaw models status
```

成功后应看到：
```
Providers w/ OAuth/tokens (1): openai-codex (1)
- openai-codex:default ok expires in 10d
```

## 三、配置模型优先级

### 3.1 设置主模型

```bash
openclaw models set openai-codex/gpt-5.4 
```

### 3.2 添加备用模型 (Fallback)

```bash
openclaw models fallbacks add glmcode/GLM-5-Turbo
```

### 3.3 验证配置

```bash
openclaw models status
```

成功后应看到：
```
Default       : openai-codex/gpt-5.4
Fallbacks (1) : glmcode/GLM-5-Turbo
Configured models (2): openai-codex/gpt-5.4, glmcode/GLM-5-Turbo
```

## 四、最终配置状态

```
🦞 OpenClaw 2026.3.11

Config        : ~/.openclaw/openclaw.json
Agent dir     : ~/.openclaw/agents/main/agent
Default       : openai-codex/gpt-5.4
Fallbacks (1) : glmcode/GLM-5-Turbo

Auth overview
Providers w/ OAuth/tokens (1): openai-codex (1)
- openai-codex:default=OAuth

OAuth/token status
- openai-codex:default ok expires in 10d
```

## 五、工作原理

| 优先级 | 模型 | 认证方式 | 用途 |
|--------|------|----------|------|
| 1 (主) | openai-codex/gpt-5.4 | OAuth | 日常使用 |
| 2 (备) | glmcode/GLM-5-Turbo | models.json | Codex 失败时自动切换 |

**故障转移逻辑**：
- OpenClaw 优先使用 Codex GPT-5.4
- 如果 Codex 出错（超限、网络问题等），自动切换到 GLM-5-Turbo
- 保证服务持续可用

## 六、常用命令

```bash
# 查看模型状态
openclaw models status

# 查看所有可用模型
openclaw models list --all

# 测试对话
openclaw chat "你好"

# 诊断问题
openclaw doctor

# 重新登录 OAuth
openclaw models auth login --provider openai-codex
```

## 七、注意事项

1. **Token 过期**：OAuth token 约 10 天过期，OpenClaw 会自动刷新，如失败需重新登录
2. **回调端口**：OAuth 使用 `127.0.0.1:1455` 端口，仅本地访问
3. **ChatGPT 订阅**：支持 ChatGPT Plus/Pro 订阅的 OAuth 认证

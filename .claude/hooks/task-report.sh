#!/usr/bin/env bash
# task-report Stop hook
# 输出 prompt 指令给 Claude，引导其生成任务执行报告
set -uo pipefail

WORK_DIR=".42cog/work"
REMOTE_FILE="$WORK_DIR/.remote_confirmed"

# 检查是否在项目根目录
if [ ! -d "$WORK_DIR" ]; then
  echo '{"ok": true}'
  exit 0
fi

# 检查远程仓库确认文件
remote_status="已确认"
if [ ! -f "$REMOTE_FILE" ]; then
  remote_status="未确认"
fi

# 获取最近报告文件（用于判断是否已生成）
latest_report=$(ls -t "$WORK_DIR"/*.md 2>/dev/null | head -1)

cat <<PROMPT_EOF
{"ok": false, "reason": "任务执行报告工作流尚未完成。请按顺序执行以下步骤：\n\n## 1. 远程仓库确认\n远程仓库状态: $remote_status\n${remote_status:-若远程仓库未确认，执行 git remote -v 检查，如无远程仓库则提示用户输入地址，如有则与用户确认地址是否正确，确认后将 URL 写入 $REMOTE_FILE}\n\n## 2. 生成任务执行报告\n使用 date '+%Y-%m-%d %H-%M' 获取时间戳。\n\n报告保存到: $WORK_DIR/\n文件名格式: yyyy-mm-dd hh-mm [操作总结].md\n\n报告必须包含以下章节：\n- 任务概述（用户要求做什么）\n- 执行过程（具体做了哪些操作，按模块/步骤组织）\n- 涉及文件（修改/创建的文件列表，建议用表格）\n- 执行结果（成功/失败，关键产出）\n- 遗留问题（如有待办事项）\n\n报告格式参考 .42cog/work/ 下的历史报告。\n\n## 3. Git 提交\n执行 /git-commit 作为收尾。"}
PROMPT_EOF

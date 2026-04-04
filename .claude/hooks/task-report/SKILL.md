---
name: task-report
description: Stop hook — 任务结束时自动生成执行报告到 .42cog/work/
category: workflow
event: Stop
language: bash
version: 1.0.0
---

# task-report

任务结束时自动拦截 Stop，生成 Markdown 格式的任务执行报告。

## 触发条件

- Claude 完成了实质性文件修改/创建工作
- 尚未生成对应的任务执行报告

## 报告格式

文件名: `yyyy-mm-dd hh-mm [操作总结].md`
保存路径: `.42cog/work/`

## 报告模板结构

```markdown
# [任务标题]

> 更新时间: yyyy-mm-dd hh:mm
> Sprint/阶段: [标识]

---

## 任务概述
[用户要求做什么]

## 执行过程
[具体做了哪些操作]

## 涉及文件
| 操作 | 文件路径 |
|------|----------|
| 修改 | path/to/file |
| 新增 | path/to/new-file |

## 执行结果
- 状态: 成功/失败
- 关键产出: [描述]

## 遗留问题（如有）
[待办事项]
```

## 工作流

1. 检查 `.42cog/work/.remote_confirmed` 是否存在
2. 生成报告并保存
3. 执行 `/git-commit`

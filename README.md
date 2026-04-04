# AI原生项目模板

这是一个基于认知敏捷法(42COG)的AI原生项目初始化模板。

## 目录结构

```
projectname/
├── .42cog/              # 认知敏捷法核心文件
│   ├── meta/            # 项目元信息
│   ├── real/            # 现实约束
│   ├── cog/             # 认知模型
│   ├── spec/            # 规约文档
│   ├── work/            # 工作记录
│   └── others/          # 其他文档
├── .42plugin/           # 插件技能库
├── .claude/             # Claude Code 配置
├── notes/               # 项目笔记和文档
├── source/              # 原始素材和资源（不纳入版本控制）
└── src/                 # 源代码目录
```

## 快速开始

1. **复制模板**
   ```bash
   cp -r project-template your-project-name
   cd your-project-name
   ```

2. **初始化项目元信息**
   编辑 `.42cog/meta/meta.md`，填写项目基本信息

3. **定义现实约束**
   编辑 `.42cog/real/real.md`，列出项目的现实约束（最多7条）

4. **创建认知模型**
   编辑 `.42cog/cog/cog.md`，定义项目的核心实体和关系

5. **生成规约文档**
   使用 `.42plugin/42edu/` 下的技能生成各类规约文档

6. **开始编码**
   在 `src/` 目录下开发代码

## 认知敏捷法 (42COG)

### RCSW 工作流

```
Real (现实约束) → Cog (认知模型) → Spec (规约文档) → Work (实际作品)
```

## 更多资源

- 认知敏捷法文档: https://github.com/42ailab/42cog
- 活水插件平台: https://42plugin.com
- 活水AI实验室: https://42ailab.com

# Python程序设计课程学伴Agent实验协作 Crew

> 基于 [crewAI](https://crewai.com) 构建的多智能体协作系统，对应实验 5 小组的 5 个分工职位，
> 用于自动产出"Python程序设计课程学伴Agent"实验的架构分析、部署测试方案、实验报告、PPT 设计、汇报稿等交付物。

## 项目背景

- 实验名称：**实验5 - Python程序设计课程学伴 Agent**
- 目标项目：`../coding-mentor-agent/`（来自 https://github.com/xixu-me/coding-mentor-agent ）
- 任务文档：`实验5.agent程序设计案例.txt`
- 实验步骤：`实验步骤.md`
- 小组分工：`小组分工/职位{1..5}-*.md`

## 5 个智能体（对应 5 个分工职位）

| 代号 | 分工职位 | 智能体 | 主要职责 |
|---|---|---|---|
| A | 架构分析师 | `架构分析师` | 梳理 7 层架构、阅读源码、绘制结构图与流程图、分析知识库 |
| B | 部署与沙箱测试员 | `部署与沙箱测试员` | 设计部署方案、6 类沙箱测试、5 类风险验证 |
| C | 实验报告撰写员 | `实验报告撰写员` | 按 7 章结构撰写 5000-8000 字报告、回答 8 个总结问题 |
| D | PPT制作员 | `PPT制作员` | 设计 12-15 页 PPT 大纲、演讲者备注、汇报速查表 |
| E | 汇报员 | `汇报员` | 撰写 8-12 分钟讲解稿、准备 15+ 个 Q&A |

## 5 个任务

1. **架构分析任务** → `output/01-架构分析.md`
2. **部署与沙箱测试任务** → `output/02-部署与沙箱测试方案.md`
3. **实验报告撰写任务** → `output/03-实验报告.md`
4. **PPT设计任务** → `output/04-PPT设计.md`
5. **汇报稿撰写任务** → `output/05-汇报稿.md`

任务之间通过 `context` 显式建立依赖：架构分析 → 部署测试 → 报告撰写 → PPT 设计 → 汇报稿。

## 自定义工具

- `项目文件读取工具`：读取 `coding-mentor-agent` 项目内的源码、配置、知识库文件。
- `知识库检索工具`：在 `kb/python-course-kb-practical-python/wiki/` 中按关键词检索概念与练习。
- `部署命令生成工具`：按阶段（环境检查/npm安装/构建沙箱镜像/启动服务/一键脚本）输出可执行的 PowerShell 命令片段。

## 安装与环境

需要 Python >= 3.10 且 < 3.14。本项目使用 [uv](https://docs.astral.sh/uv/) 进行依赖管理。

```bash
# 安装 uv（如未安装）
pip install uv

# 安装项目依赖
uv sync
```

## 配置

复制并按需修改 `.env`：

```ini
# 大语言模型 API 密钥（必填）
OPENAI_API_KEY=your-key-here

# 目标项目根目录（指向 coding-mentor-agent）
TARGET_PROJECT_ROOT=../coding-mentor-agent
```

## 运行

在项目根目录执行：

```bash
crewai run
```

或直接：

```bash
uv run python -m myflow.main
```

执行完成后，5 份实验材料会按顺序落盘到 `output/` 目录。

## Flow 可视化

```bash
uv run python -m myflow.main plot
```

将在当前目录生成 `实验协作Flow.html`，可用浏览器打开查看流程图。

## 触发器模式

通过 JSON 触发器自定义项目路径：

```bash
uv run python -m myflow.main '{"项目路径": "D:/projects/coding-mentor-agent"}'
```

## 项目结构

```
.
├── .env                          # 环境变量（OPENAI_API_KEY、TARGET_PROJECT_ROOT）
├── pyproject.toml                # 项目元数据与依赖
├── README.md                     # 本文件
├── AGENTS.md                     # CrewAI 编码助手参考
├── 实验5.agent程序设计案例.txt    # 实验任务文档
├── 实验步骤.md                   # 实验步骤文档
├── 小组分工/                     # 5 个职位的工作描述
├── coding-mentor-agent/          # 目标项目（来自外部仓库）
└── src/myflow/
    ├── main.py                   # Flow 入口（实验协作Flow）
    ├── crews/
    │   └── content_crew/         # 实验协作 Crew
    │       ├── content_crew.py
    │       └── config/
    │           ├── agents.yaml   # 5 个 Agent 的角色/目标/背景故事
    │           └── tasks.yaml    # 5 个任务的描述/期望输出
    └── tools/
        └── custom_tool.py        # 3 个中文自定义工具
```

## 与实验材料的对应关系

| 实验材料 | Crew 产出 | 对应 Agent |
|---|---|---|
| 小组分工/A-产出/05-架构分析文档.md | `output/01-架构分析.md` | 架构分析师 |
| 小组分工/B-产出/04-沙箱测试记录.md | `output/02-部署与沙箱测试方案.md` | 部署与沙箱测试员 |
| 小组报告/实验报告.md | `output/03-实验报告.md` | 实验报告撰写员 |
| 小组报告/实验PPT.pptx 大纲 | `output/04-PPT设计.md` | PPT制作员 |
| 小组分工/E-产出/02-讲解稿.md | `output/05-汇报稿.md` | 汇报员 |

Crew 产出的 5 份 Markdown 可作为各职位人工撰写的"草稿/参考"。

## 许可与致谢

- CrewAI 框架：[https://crewai.com](https://crewai.com)
- 目标项目：[https://github.com/xixu-me/coding-mentor-agent](https://github.com/xixu-me/coding-mentor-agent)
- 本协作 Crew 仅作为实验辅助工具，最终实验成果以小组成员的人工产出为准。

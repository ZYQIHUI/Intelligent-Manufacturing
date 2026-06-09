# AI 开发技术 — 小组实验仓库

本仓库收录《AI开发技术》课程的五次小组实验，涵盖从基础图像识别到复杂多智能体系统的完整实践链路：

|实验 |主题 |技术栈 |
|---|---|---|
|实验一 |前端 Streamlit 手写体识别 MNIST |PyTorch / TensorFlow, Streamlit, pytest |
|实验二 |数据分析——就业状态分析与预测 |Pandas, Scikit-learn, XGBoost, Claude Code Skills |
|实验三 |基于 RAG 的复杂 PDF 智能问答系统 |RAG, LLM, Prompt / Skill 双方案 |
|实验四 |医学图像技术调研 |眼底病变分割、医学图像增强文献综述 |
|实验五 |Agent 程序设计案例——Python 编程学习助手 |TypeScript, React, Node.js, Docker, CrewAI, SQLite |

## 实验一 — 手写体识别 MNIST

```
AI开发技术-实验1-前端streamlit的手写体识别mnist/
├── Agent+Skills/       # PyTorch 主实现 (app.py, train.py, mnist/, tests/, model.pth)
├── 使用prompt/         # TensorFlow 备选 (app.py, train.py, mnist_model.h5)
├── docs/               # 开发计划、对话记录
├── Images/             # 文档截图
├── presentation/       # 实验 PPT
├── report/             # 实验报告 (.docx)
├── videos/             # 演示视频 (A.mp4, B.mp4)
├── 了解前提/           # Jupyter / Streamlit 前置学习
├── README.md
└── requirements.txt
```

## 实验二 — 就业状态分析与预测

```
AI开发技术-实验2-数据分析/
├── 相关源码/           # 完整源码 (prompt版 + skill版 + .claude/ Skills)
├── 技术报告模板/       # LaTeX 模板 (cumcmthesis)
├── 附件1 数据.xls      # 宜昌 5000 份就业调查原始数据
├── explore_data.py     # 数据探索脚本
├── 项目说明.md
├── 自定义Skill创建过程.md
├── AI驱动的就业状态分析与预测.pptx
├── AI驱动的就业状态分析与预测实验报告.docx   # 实验报告
├── AI驱动的就业状态分析与预测——数据分析实验报告.docx  # 数据分析报告
├── PPT大纲.md
├── 题目-就业状态分析与预测.pdf          # 竞赛题目
├── 技术报告范例_decrypted.pdf           # 参考范例
├── 技术报告范例（密码123456）.pdf
├── AI开发技术-实验2-数据分析.txt        # 实验说明
└── AGENT.md
```

## 实验三 — RAG 智能问答系统

```
AI开发技术-实验3-基于RAG的复杂pdf文档智能问答系统/
├── PromptVersion/      # Prompt 版 RAG 源码
├── SkillVersion/       # Skill 版模块化 RAG 源码
├── 提交内容/           # 最终提交物 (prompt.md, skills.zip, 视频, 报告, PPT)
├── docs/               # 说明文档、测试记录、方案对比
├── videos/             # Prompt演示.mp4, Skill演示.mp4
├── 实验记录(图片)/     # 流程图、问答截图
├── 技能清单/           # 技能概览
├── 金融研报.pdf        # 示例 PDF 文档
├── README.md
└── requirements.txt
```

## 实验四 — 医学图像技术调研

```
AI开发技术-实验4-实验要求-医学图像技术调研/
├── deliverables/       # 技术调研报告 (.docx)
├── approach-prompt/    # Prompt 方式调研过程
├── approach-skill/     # Skill 方式调研过程
├── SkillV/             # Skill 版本输出
├── docs/               # 实验要求、笔记
└── papers/
    ├── 眼底视网膜病变分割/  # 2020-2025 论文 (9 篇)
    ├── 医学图像增强/        # 2024-2026 论文 (5 篇)
    ├── SAM模型蒸馏/
    └── SAM相关/
```

## 实验五 — Agent 程序设计案例

```
AI开发技术-实验5-agent程序设计案例/
├── coding-mentor-agent/        # Python 学伴 Agent (TypeScript 全栈)
│   ├── src/{frontend,server,agent,tools,sandbox,db,security}
│   ├── tests/                   # 30+ 测试 (含 E2E)
│   └── kb/                      # Python 课程知识库
├── docs/                        # 源码分析、实验步骤、问题记录
├── src/myflow/                  # CrewAI Flow 编排 (agents.yaml, tasks.yaml)
├── output/                      # CrewAI 自动产出文档
├── AI-开发技术实验5-学伴Agent/  # 补充文档 + 截图
├── 小组分工/                    # 5 角色分工文档
├── README.md
└── pyproject.toml
```



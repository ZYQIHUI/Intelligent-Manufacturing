# 项目所需技能清单

> **项目**：AI技术-实验4.1-医学图像技术调研
> **主题**：SAM在医学图像分割中的应用 → 聚焦眼底视网膜病变分割
> **两种执行方式**：提示词方式 vs Skill方式


---

## 快速安装指南

`ash

# 在项目根目录下执行，一键安装所有所需技能

codex skills install deep-research
codex skills install academic-pipeline
codex skills install nature-reader
codex skills install nature-writing
codex skills install nature-citation
codex skills install nature-paper2ppt
codex skills install docx
codex skills install pptx
codex skills install pdf
codex skills install search-skills-for-user
`

> **注意**：nature系列技能来自 https://github.com/Yuan1z0825/nature-skills
> academic系列技能来自 https://github.com/Imbad0202/academic-research-skills


---

## 技能清单

### 🔬 核心研究技能（3个）

|技能 |用途 |所属仓库 |调用阶段 |
|---|---|---|---|
|deep-research |SOTA调研、问题分析、实验方案设计 |skill-installer内置 |调研阶段 |
|academic-pipeline |完整学术管线编排（10阶段） |skill-installer内置 |全过程 |
|nature-reader |论文PDF读取，中英文对照解读 |nature-skills |论文分析 |

### 📄 报告与文档技能（4个）

|技能 |用途 |所属仓库 |调用阶段 |
|---|---|---|---|
|nature-writing |生成Nature风格报告章节 |nature-skills |报告生成 |
|nature-citation |Nature/CNS格式引用管理 |nature-skills |报告生成 |
|docx |创建/编辑Word文档 |skill-installer内置 |最终产出 |
|pdf |PDF文件读取与提取 |skill-installer内置 |论文分析 |

### 📊 演示技能（2个）

|技能 |用途 |所属仓库 |调用阶段 |
|---|---|---|---|
|nature-paper2ppt |从报告生成中文PPT |nature-skills |最终产出 |
|pptx |演示文稿创建与编辑 |skill-installer内置 |最终产出 |

### 🛠 辅助技能（1个）

|技能 |用途 |所属仓库 |调用阶段 |
|---|---|---|---|
|search-skills-for-user |搜索SkillsMP发现其他技能 |search-ppt skill |准备阶段 |


---

## 任务阶段与技能映射

### 阶段一：准备工作

安装技能 → 浏览论文 → 理解任务

- 使用：search-skills-for-user, pdf, nature-reader

### 阶段二：方式1 - 提示词方式

4轮Prompt：SOTA调研 → 问题分析 → 实验蓝图 → 生成报告

- 文件位置：approach-prompt/prompts/
- 无需调用技能，直接与AI对话

### 阶段三：方式2 - Skill方式

1. deep-research → SOTA方法调研
2. deep-research → 问题与不足分析
3. deep-research → 实验蓝图设计
4. nature-writing → 按提纲生成报告

- 文件位置：approach-skill/Plan.md

### 阶段四：对比分析

从效率、质量、透明度、灵活性四个维度对比

### 阶段五：最终产出

- docx → 转Word报告 → deliverables/技术调研报告.docx
- nature-paper2ppt / pptx → 生成调研PPT


---

## 团队分工建议

|成员 |负责内容 |
|---|---|
|成员A |方式1（提示词方式）：4轮Prompt执行与记录 |
|成员B |方式2（Skill方式）：调用技能自动化完成调研 |
|成员C |论文阅读与资料整理 |
|全员 |对比分析、报告整合、PPT制作 |

## 产出物检查清单

- [ ] 技术调研报告（Word） → deliverables/
- [ ] 调研PPT → deliverables/
- [ ] 实验总结（含心得体会）
- [ ] Agent任务拆解轨迹记录
- [ ] Skill调用情况记录
- [ ] 两种方式对比分析


---

## 项目文件结构

`项目根目录/ ├── docs/                     # 项目文档 │   ├── 实验要求-AI技术-实验4.1.txt │   ├── NeedSkills.md         # ← 本文件（技能清单） │   └── PChat.md ├── papers/                   # 论文资料（4类） ├── approach-prompt/          # 方式1：提示词方式 │   ├── prompts/              # 4轮Prompt │   └── responses/            # 3轮响应 ├── approach-skill/           # 方式2：Skill方式 │   └── Plan.md               # 执行计划 └── deliverables/             # 最终产出     └── 技术调研报告.docx`
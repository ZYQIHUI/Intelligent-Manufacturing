# 实验二 — 数据分析：就业状态分析与预测

基于 2024 年第 17 届"华中杯"C 题——宜昌市 5000 份居民就业调查数据（53 变量），进行就业状态分析与预测。

## 技术栈

Pandas, Scikit-learn, XGBoost, LightGBM, LaTeX, Claude Code Custom Skills

## 核心内容

- **Prompt 驱动版 + Skill 增强版** — 完整源码归档于 `相关源码/`
- **自定义 Skill** (`相关源码/.claude/skills/`) — data-modeling-pipeline, latex-report-generator
- **数据文件** — `附件1 数据.xls`（原始问卷数据，含训练集与预测集）
- **技术报告** — 基于 cumcmthesis LaTeX 模板生成的完整报告

## 目录结构

```
相关源码/                            # 完整源码 (prompt版 + skill版 + .claude Skills)
技术报告模板/                         # LaTeX cumcmthesis 模板
附件1 数据.xls                        # 原始调查数据 (宜昌 5000 份, 53 变量)
explore_data.py                       # 数据探索脚本
项目说明.md                            # 项目概述
自定义Skill创建过程.md                 # Skill 开发记录
AI驱动的就业状态分析与预测.pptx         # 答辩 PPT
AI驱动的就业状态分析与预测实验报告.docx   # 实验报告 (完整版 58KB)
AI驱动的就业状态分析与预测——数据分析实验报告.docx  # 数据分析报告 (简版 11KB)
PPT大纲.md                             # PPT 大纲与分工
题目-就业状态分析与预测.pdf             # 竞赛题目原文
技术报告范例_decrypted.pdf              # 技术报告参考范例
技术报告范例（密码123456）.pdf           # 技术报告参考范例 (加密)
AI开发技术-实验2-数据分析.txt           # 实验说明与参考资料
AGENT.md                               # Claude Code 项目配置
```

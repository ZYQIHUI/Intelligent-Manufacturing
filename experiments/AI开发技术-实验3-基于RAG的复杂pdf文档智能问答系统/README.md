# 实验三 — 基于 RAG 的复杂 PDF 文档智能问答系统

针对复杂 PDF 文档（以金融研报为例）构建检索增强生成（RAG）智能问答系统，对比 Prompt 与 Skill 两种实现方案。

## 技术栈

RAG, LLM, Milvus, Sentence-Transformers, Streamlit

## 核心内容

- **Prompt 版** (`PromptVersion/`) — app.py, build_kb.py, test_questions.py
- **Skill 版** (`SkillVersion/`) — 模块化实现：pdf_parser, embedding_engine, vector_store, config
- **最终提交** (`提交内容/`) — prompt.md, skills.zip, 演示视频, 实验报告, PPT
- **示例文档** — `金融研报.pdf`（RAG 问答对象）

## 目录说明

| 目录/文件 | 说明 |
|-----------|------|
| `PromptVersion/` | Prompt 版 RAG 源码及向量数据库 |
| `SkillVersion/` | Skill 版模块化 RAG 源码 |
| `提交内容/` | 最终提交物（提示词、Skill 包、视频、报告、PPT） |
| `金融研报.pdf` | 示例 PDF 文档 |
| `Prompt演示.mp4` / `Skill演示.mp4` | 方案演示视频 |
| `实验记录(图片)/` | Venn 图、阶段对比图等 |
| `推荐方案.md` / `问答测试.md` | 方案评估与测试记录 |

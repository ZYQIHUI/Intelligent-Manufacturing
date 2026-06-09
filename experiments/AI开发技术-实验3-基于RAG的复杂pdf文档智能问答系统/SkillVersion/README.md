# SkillVersion — 基于 RAG 的复杂 PDF 文档智能问答系统

社区 Skill + 自定义 Skill 协同生成版本。

## 技能体系

| 模块 | Skill | 来源 | 说明 |
|------|-------|------|------|
| PDF 解析 | `pdf-parser` | 自定义（MySkills） | PyMuPDF + EasyOCR，针对中文金融 PDF 优化 |
| RAG 检索 | `rag-implementation` | 社区（claude-plugins） | 嵌入选择 → 分块 → 检索 → LLM 集成的完整工作流 |
| 向量数据库 | `rag-implementation` Phase 3+5 | 社区 | Milvus Lite 双集合设计，COSINE 相似度 |
| 前端界面 | `frontend-design` | 社区（anthropics/skills） | "暗金金融终端"主题，生产级 UI 质量 |

## 快速开始

### 1. 环境准备

```bash
# 激活虚拟环境
source venv/Scripts/activate   # Windows Git Bash
# 或
venv\Scripts\activate          # Windows CMD

# 安装依赖
pip install -r requirements.txt
```

### 2. 配置 API Key

编辑项目根目录的 `.env` 文件：

```env
DEEPSEEK_API_KEY=sk-xxxx...
DEEPSEEK_BASE_URL=https://api.deepseek.com
DEEPSEEK_MODEL=deepseek-chat
```

### 3. 构建知识库

```bash
python SkillVersion/build_kb.py
```

首次运行会自动下载 EasyOCR 模型（~100MB）和 BGE 嵌入模型。

### 4. 启动问答界面

```bash
streamlit run SkillVersion/app.py
```

浏览器访问 `http://localhost:8501`。

### 5. 运行测试

```bash
python SkillVersion/test_questions.py
```

## 项目结构

```
SkillVersion/
├── config.py              # 全局配置：路径、模型、分块参数、检索参数
├── pdf_parser.py           # PDF 解析器：PyMuPDF 文本 + EasyOCR 图片识别
├── embedding_engine.py     # 嵌入引擎：BAAI/bge-small-zh-v1.5 向量化
├── vector_store.py         # 向量存储：Milvus Lite 双集合（text + image）
├── build_kb.py             # 知识库构建编排脚本
├── app.py                  # Streamlit Web 前端
└── test_questions.py       # 4 道样本题自动化测试
```

## 技术栈

| 组件 | 技术选型 |
|------|---------|
| PDF 文本提取 | PyMuPDF (fitz) |
| 图片 OCR | EasyOCR（ch_sim + en） |
| 文本分块 | LlamaIndex SentenceSplitter（chunk=512, overlap=50） |
| 嵌入模型 | BAAI/bge-small-zh-v1.5（512 维） |
| 向量数据库 | Milvus Lite（嵌入式，COSINE 距离） |
| 大语言模型 | DeepSeek-Chat（OpenAI 兼容 API） |
| 前端框架 | Streamlit |

## 检索策略

- **文本集合**：取 top_k 条（默认 8 条）
- **图片集合**：取 top_k // 2 条（默认 4 条）
- **合并规则**：文本结果在前，图片结果在后，去重合并
- **不按分数混合排序**，避免 OCR 碎片文本的向量分数系统性偏高

## 设计系统

前端采用 **"暗金金融终端"** 设计主题：

- **色彩**：深色底色（#0d1117）+ 暖金点缀（#d4a853）
- **字体**：Playfair Display（标题）+ JetBrains Mono（代码/数据）+ Noto Sans SC（正文）
- **交互**：金色边框聚焦高亮、悬停过渡动画

## 设计理念

SkillVersion 的核心目标是验证 **社区通用 Skill + 项目特定 Skill 协同工作**的可行性：

- `rag-implementation` 提供通用 RAG 工作流框架（Phase 1-8）
- `frontend-design` 提供前端设计方法论和审美标准
- `pdf-parser`（自定义）提供本项目特有的中文金融 PDF 解析经验

与完全自定义 Skill 的开发方式对比，本版本引入了社区 Skill 作为架构和设计指引，减少了从零定义架构的负担。

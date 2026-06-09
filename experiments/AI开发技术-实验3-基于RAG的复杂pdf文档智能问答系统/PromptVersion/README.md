# PDF 智能问答系统 — 阶段一：单提示词生成

基于 **LlamaIndex + Milvus Lite + DeepSeek** 的 RAG 复杂 PDF 文档智能问答系统。

## 项目结构

```
PromptVersion/
├── prompt.txt      # 原始提示词
├── build_kb.py     # 知识库构建器（PDF解析 → 向量化 → Milvus存储）
├── app.py          # Streamlit 智能问答前端
└── README.md       # 本文件

../                  # 项目根目录
├── .env            # API Key 等环境配置
├── requirements.txt
├── setup.bat / setup.sh
└── 金融研报.pdf    # 源 PDF 文档
```

## 快速开始

### 1. 环境安装

```bash
# Windows
setup.bat

# Linux / Mac
bash setup.sh
```

或手动安装：

```bash
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r ../requirements.txt
```

### 2. 配置 API Key

编辑根目录 `.env` 文件，填入 DeepSeek API Key：

```
DEEPSEEK_API_KEY=sk-你的key
```

### 3. 构建知识库

```bash
python PromptVersion/build_kb.py
```

脚本会：
- 解析 PDF 中的文本、表格、图片
- 对图片运行 EasyOCR 提取文字
- 用 BAAI/bge-small-zh-v1.5 向量化
- 按 文本/表格/图片 三类分别存入 Milvus Lite

### 4. 启动问答界面

```bash
streamlit run PromptVersion/app.py
```

浏览器打开 `http://localhost:8501` 即可使用。

## 技术架构

| 组件 | 技术选型 | 说明 |
|------|---------|------|
| PDF 解析 | pdfplumber + PyMuPDF | 文本/表格/图片分离提取 |
| 图片 OCR | EasyOCR | 中英文混合识别 |
| 文本分块 | LlamaIndex SentenceSplitter | 512 token，50 重叠 |
| 向量化 | BAAI/bge-small-zh-v1.5 | 512 维，中文金融文本优化 |
| 向量存储 | Milvus Lite | 嵌入式，文本/表格/图片三个独立集合 |
| 大模型 | DeepSeek-Chat | OpenAI 兼容 API |
| 前端 | Streamlit | 聊天界面 + 配置面板 |

## 界面功能

- **连接状态栏**：实时显示 API 和数据库是否就绪
- **侧边栏设置**：修改 API Key、切换模型、上传新 PDF
- **数据库统计**：显示文本/表格/图片三类向量数量
- **多轮对话**：支持上下文连续问答
- **参考来源**：每条回答附带检索来源（页码 + 相似度）
- **错误提示**：API 未配置、知识库为空等情况给出明确指引

## 检索策略

用户提问时，同时检索三个向量集合（文本/表格/图片），合并排序后作为上下文提供给 DeepSeek。对于表格数据查询（如"沪深300开盘价"）和图表信息查询，能自动命中对应的表格/图片向量，保证数据类问题的准确回答。

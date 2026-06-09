# AI 开发技术 — 实验1：Streamlit 手写体识别 MNIST

> 本项目通过 **两种方法** 构建 MNIST 手写数字识别系统：
>
> - **方法 A**：纯提示词驱动（`使用prompt/`）
> - **方法 B**：Agent + Skills 驱动 + TDD（`Agent+Skills/`）


---

## 📂 完整目录结构

```text
AI开发技术-实验1-前端streamlit的手写体识别mnist/
│
├── 📄 README.md                                    ← 本文件：项目总览
├── 📄 AI开发技术-实验1-前端streamlit的手写体识别mnist.txt  ← 实验要求说明书
├── 📄 随记(这个不重要).md                            ← 开发过程中的随记
│
├── 📁 使用prompt/                    ← 方法A：纯提示词驱动（TensorFlow / Keras）
│   ├── 📄 train.py                  ┊ CNN 训练脚本（99.29% 准确率）
│   ├── 📄 app.py                    ┊ Streamlit 前端（上传图片 + 手写画布）
│   ├── 📄 mnist_model.h5            ┊ 训练好的模型权重（~2.7 MB）
│   ├── 🖼️ training_curves.png       ┊ 训练曲线图（准确率 + 损失）
│   └── 📄 prompt_chat.txt           ┊ 完整对话记录（4轮交互）
│
├── 📁 Agent+Skills/                 ← 方法B：Agent + Skills 驱动（PyTorch + TDD）
│   │
│   │── 📄 requirements.txt          ┊ 依赖清单
│   │── 📄 train.py                  ┊ 训练入口脚本
│   │── 📄 evaluate.py               ┊ 评估入口脚本
│   │── 📄 run_all_tests.py          ┊ 一键运行全部 10 个 TDD 测试
│   │── 📄 model.pth                 ┊ 训练好的模型权重（99.31%，~400K 参数）
│   │── 📄 app.py                    ┊ Streamlit 前端（画板 + 上传 + 概率条形图）
│   │── 📄 对话记录.txt               ┊ 完整开发对话记录
│   │── 🖼️ test.png                  ┊ 测试用示例图片
│   │── 📄 _run_fix.bat              ┊ 快速修复脚本
│   │
│   ├── 📁 mnist/                    ┊ 核心 Python 包
│   │   ├── 📄 __init__.py           ┊ 包初始化
│   │   ├── 📄 data.py               ┊ load_data() — 加载 MNIST，返回 DataLoader
│   │   ├── 📄 model.py              ┊ MNISTCNN 类 — 2 层卷积 CNN
│   │   ├── 📄 train.py              ┊ train_one_epoch() — 单轮训练逻辑
│   │   └── 📄 evaluate.py           ┊ evaluate() + predict_image() — 评估 + 预测
│   │
│   ├── 📁 tests/                    ┊ TDD 测试套件（10 个测试全部通过 ✅）
│   │   ├── 📄 test_data.py          ┊ 4 个测试：形状 / 标签范围 / 归一化 / 返回值
│   │   ├── 📄 test_model.py         ┊ 4 个测试：前向形状 / 概率分布 / 参数量 / 保存加载
│   │   └── 📄 test_train.py         ┊ 2 个测试：单轮训练 / 损失下降
│   │
│   ├── 📁 data/                     ┊ MNIST 数据集（自动下载）
│   │   └── MNIST/raw/
│   │       ├── train-images-idx3-ubyte   ┊ 训练集图片（60,000 张）
│   │       ├── train-labels-idx1-ubyte   ┊ 训练集标签
│   │       ├── t10k-images-idx3-ubyte    ┊ 测试集图片（10,000 张）
│   │       └── t10k-labels-idx1-ubyte    ┊ 测试集标签
│   │
│   └── 📁 .pytest_cache/            ┊ pytest 缓存（自动生成）
│
├── 📁 Images/                       ← 实验报告截图素材（共 22 张）
│   ├── 🖼️ AgentSkills目录.png
│   ├── 🖼️ Streamlit界面.png
│   ├── 🖼️ pytest测试结果.png
│   ├── 🖼️ pytest退出码说明.png
│   ├── 🖼️ 全部测试通过.png
│   ├── 🖼️ 列出项目目录.png
│   ├── 🖼️ 创建应用提示.png
│   ├── 🖼️ 启动Streamlit.png
│   ├── 🖼️ 扩展程序列表.png
│   ├── 🖼️ 模型结构说明.png
│   ├── 🖼️ 模型训练参数配置.png
│   ├── 🖼️ 编写实施计划.png
│   ├── 🖼️ 训练数据下载.png
│   ├── 🖼️ 评估任务范围.png
│   ├── 🖼️ 评估前端文件.png
│   ├── 🖼️ 读取项目文件.png
│   ├── 🖼️ 运行统计与合并.png
│   ├── 🖼️ 运行评估与前端.png
│   ├── 🖼️ 部署上传图片.png
│   ├── 🖼️ 部署手写输入.png
│   ├── 🖼️ 项目文件列表.png
│   └── 🖼️ 项目目录结构.png
│
├── 📁 docs/                         ← 实施计划文档
│   └── superpowers/plans/
│       └── 📄 MNIST-PyTorch-TDD-Plan.md   ← 8 个 Task 的详细 TDD 实施计划
│
└── 📁 使用prompt（独立副本）/
    ├── 📄 app.py                    ← Streamlit 前端
    ├── 📄 train.py                  ← 训练脚本
    └── 📄 mnist_model.h5            ← 模型权重
```


---

## ⚔️ 两种方法对比一览

|对比维度 |`使用prompt/`（方法 A） |`Agent+Skills/`（方法 B） |
|:---|:---|:---|
|**开发方式** |纯提示词，手动多轮交互 |Agent 自动调用多个 Skill 协作完成 |
|**AI 框架** |TensorFlow + Keras |PyTorch |
|**开发方法** |直接编写代码 |**TDD**（测试驱动开发）— 先写测试，再写实现 |
|**自动化测试** |❌ 无 |✅ 10 个自动化测试，覆盖数据 / 模型 / 训练 |
|**项目结构** |2 个文件平铺 |模块化包（`mnist/`）+ 独立测试目录（`tests/`） |
|**前端画布** |`st.image` + 文件上传 |`streamlit-drawable-canvas` 画板组件 |
|**概率展示** |仅显示最高置信度 |**条形图**展示 0–9 全部概率分布 |
|**代码质量** |脚本式，无复用设计 |函数式模块化，可复用、可测试 |
|**文档完备度** |对话记录（`prompt_chat.txt`） |对话记录 + 实施计划（`MNIST-PyTorch-TDD-Plan.md`） |
|**测试准确率** |**99.29%** |**99.31%** |


---

## 🔧 快速启动

### 方法 A（TensorFlow）

```bash
cd 使用prompt
pip install tensorflow streamlit pillow opencv-python
streamlit run app.py
```

### 方法 B（PyTorch）

```bash
cd Agent+Skills
pip install -r requirements.txt
streamlit run app.py
```

### 运行测试（仅方法 B）

```bash
cd Agent+Skills
python -m pytest tests/ -v
```


---

## 📝 实验目的

1. 掌握利用 AI Agent 辅助开发 **Streamlit 前端应用** 的能力
2. 对比 **纯提示词驱动** 与 **Agent + Skills + TDD** 两种开发路线的优劣
3. 体验 **测试驱动开发（TDD）** 在 AI 辅助编程中的实际效果



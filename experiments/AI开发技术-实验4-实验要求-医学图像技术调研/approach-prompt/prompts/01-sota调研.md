# 🎯 第①轮提示词：SOTA 方法调研（粘贴给 Gemini）

你现在是一位顶尖的医学图像分析研究员，专攻眼底视网膜病变分割方向。请帮我完成以下调研任务。

---

## 调研主题
基于 SAM（Segment Anything Model）的眼底视网膜病变分割 — SOTA 方法综述

---

## 请帮我回答以下问题

### 1️⃣ 有哪些 SOTA 方法？
基于 SAM 的眼底视网膜病变分割领域有哪些主流方法？分别列出：
- 方法名称、提出年份、所属机构
- 核心创新点是什么？（用一两句话说清楚）
- 哪些是专门针对医学/眼底图像的？哪些是通用分割模型迁移过来的？

### 2️⃣ 用了什么数据集？
常用的公开数据集有哪些？简要说明：
- 数据集名称（如 IDRiD、DDR、DRIVE 等）
- 图像数量、标注了哪些病变类型、分辨率

### 3️⃣ 常用评估指标？
- 用了哪些指标？（Dice、IoU、ACC、Sensitivity、Specificity 等）
- 每个指标衡量的是分割的哪个方面？

### 4️⃣ 性能对比
- 这些方法在相同数据集（比如 IDRiD 或 DDR）上表现如何？
- 能不能给我一个性能对比表格？
- 哪个方法效果最好？为什么？

### 5️⃣ 当前趋势与问题
- 这个领域现在的研究热点是什么？
- 还有哪些关键问题没解决？

---

## 我手头有的论文（按类别整理）

> ⚠️ 我无法直接上传文件夹，以下是论文按类别整理的信息，请结合你的知识进行分析。

### 📁 SAM相关（9篇）
核心 SAM 系列，包括原始 SAM 及其医学适配版本
- SAM (Kirillov et al., 2023) — 原始 SAM 模型，SA-1B 数据集
- SAM 2 (Ravi et al., 2024) — SAM 升级版，支持视频
- MedSAM (Ma et al., 2024) — 通用医学图像分割
- Medical SAM Adapter (Wu et al., 2024) — 轻量化适配，仅调2%参数
- SAM-Med2D (Cheng et al., 2023) — 医学图像微调版
- HQ-SAM (Ke et al., 2024) — 高质量分割
- FastSAM (Zhao et al., 2023) — 实时版本
- Semantic-SAM (Li et al., 2023) — 语义分割版
- Segment Anything Model for Medical Images — 医学图像综述

### 📁 眼底视网膜病变分割（9篇）
直接针对眼底病变分割任务的方法
- RTNet (Li et al., 2022) — 关系Transformer，DR多病变分割
- GlanceSeg (Wang et al., 2023) — SAM + 注视图，微动脉瘤分割
- DeepLabv3+ (2025) — 用于DR病变分割
- SAT-Net (Zhang et al., 2024) — 结构感知Transformer，低质量眼底增强
- Lesion-aware Network (2024) — 病变感知网络
- 其他：Improving Lesion Segmentation (2020)、Deep learning for DR detection (2021, 2023)、Integrated deep learning (2024)

### 📁 医学图像增强（5篇）
提升眼底图像质量的预处理方法
- All-In-One Medical Image Restoration (2024) — 任务自适应路由
- DiffCode (2025) — 扩散模型做图像恢复
- TAT (2025) — 任务自适应Transformer
- MedSR-Vision (2026) — 多域超分辨率
- Challenges & Evaluation Metrics Review (2025) — 医学图像增强综述

### 📁 SAM模型蒸馏（6篇）
SAM 轻量化/蒸馏方法，适合部署
- MobileSAM (Zhang et al., 2023) — 移动端部署
- EfficientSAM (Xiong et al., 2024) — 高效版本
- EdgeSAM (Gong et al., 2023) — 边缘端推理
- TinySAM (Shu et al., 2023) — 极小模型
- SAM-Lightening (2024) — SAM加速
- KD-SAM (2025) — 知识蒸馏用于医学图像分割

---

## 输出要求
- **中文回答**，专业术语保留英文（括号给中文）
- **方法对比用表格**
- 每个方法标注参考文献（作者, 年份）
- 分小节，层次清晰

谢谢！

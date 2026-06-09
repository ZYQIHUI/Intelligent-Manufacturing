# 医学图像技术调研实验 - 完整执行计划

## 实验概述

**主题**：SAM在医学图像分割中的应用 -> 聚焦眼底视网膜病变分割

**核心任务**：用两种方式（提示词 vs Skill）完成同一调研课题，在关键节点对比，最后整体总结差异。

**产出物**：
1. 技术调研报告（Markdown 转 Word）
2. 调研 PPT
3. 实验总结（含对比分析、心得体会）

---

## 阶段一：准备工作（已完成）

- 读取实验要求文件，明确任务
- 探索论文文件夹结构（4类、28篇论文）
- 用 PyMuPDF 读取关键论文摘要（SAM、MedSAM、SAM-Adapter、RTNet、GlanceSeg、DeepLabv3+、SAT-Net、KD-SAM 等）
- 安装调研 Skills：[deep-research]、[academic-pipeline]、[nature-writing]、[nature-paper2ppt]、[nature-reader]、[nature-citation]、[docx]、[pptx]、[pdf]、[search-skills-for-user]

---

## 阶段二：方式1 - 提示词方式（4轮）

### 第1轮：调研 SOTA 方法

**提示词 1**：
> 现在眼底视网膜病变分割领域，基于 SAM 的 SOTA 方法有哪些？使用的评估指标和数据集有哪些？详细分析这些方法的创新点和性能对比。

**内容来源**：已读取的论文（SAM、MedSAM、SAM-Adapter、SAM-Med2D、GlanceSeg、RTNet、DeepLabv3+等）

**产出**：SOTA 方法对比表（方法名、年份、创新点、数据集、评估指标、性能）

### 第2轮：提问题

**提示词 2**：
> 当前 SAM 应用于眼底视网膜病变分割存在哪些问题与不足？重点分析：
> a) SAM 迁移到医学图像/眼底图像的适配问题
> b) 眼底图像质量较低对分割的影响
> 此外，裂缝检测、骨架检测等相似领域（细长物体检测）存在哪些类似问题？它们是如何解决的？是否可以迁移到眼底视网膜分割？

**内容来源**：已读论文中的现有局限 + 跨领域迁移分析

**产出**：问题清单 + 跨领域迁移方案表

### 第3轮：实验蓝图

**提示词 3**：
> 基于以上分析，请设计一个完整的实验方案：
> 1) 选择哪个模型作为 baseline 最合适？（要求接近 SOTA 或就是 SOTA）
> 2) 详细讲解该模型的架构和原理
> 3) 根据改进思路，如何在 baseline 上实施改进？
> 4) 使用哪个数据集（IDRiD/DDR）？评估指标？实验配置？

**产出**：完整实验设计方案

### 第4轮：生成报告

**提示词 4**：
> 将以上所有内容整合，按以下提纲生成图文并茂的技术调研报告：
> a) 研究背景与现状
> b) 存在的问题
> c) 研究方案
> d) 实验规划
> e) 参考文献

**产出**：Markdown 格式的报告初稿

---

## 阶段三：方式2 - 使用 Skill 方式

用已安装的 Skill 重复上述过程：

### 第1步：用 deep-research 调研

触发 deep-research：
> Research the application of SAM in retinal fundus lesion segmentation, covering SOTA methods, datasets (IDRiD, DDR), and evaluation metrics.

### 第2步：用 deep-research 分析问题

触发 deep research 模式，分析现有问题和跨领域迁移方案。

### 第3步：用 deep-research 设计实验

触发 deep research 模式，生成实验蓝图。

### 第4步：用 nature-writing 生成报告

使用 nature-writing 按提纲生成完整的调研报告。

---

## 阶段四：关键节点对比

在以下节点记录两种方式的差异：

| 对比维度 | 对比内容 |
|---|---|
| 效率 | 完成每个步骤所需的时间和交互次数 |
| 结果质量 | 哪个方式的分析更全面、更深入？ |
| 流程透明度 | 提示词方式（逐轮可见）vs Skill方式（黑盒自动化） |
| 灵活性 | 哪种方式更容易中途调整方向？ |

---

## 阶段五：最终产出生成

1. 最终技术调研报告：将 Markdown 转为 Word 文档（docx Skill）
2. 调研 PPT：用 nature-paper2ppt 生成
3. 实验总结：整理完整的 Agent 任务拆解轨迹、Skill 调用记录、心得体会、两种方式对比分析

---

## 关键假设

- 报告语言：中文（术语保留英文）
- 对比方式：关键节点穿插对比，最后整体总结
- 报告格式：Markdown 写 转 Word
- 所有操作在 Codex CLI 中完成

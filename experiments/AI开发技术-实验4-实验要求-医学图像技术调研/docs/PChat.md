# PChat.md — 聊天记录概括

## 实验信息
- **实验**: AI技术-实验4.1-医学图像技术调研
- **主题**: SAM在医学图像分割中的应用 → 聚焦眼底视网膜病变分割
- **工作目录**: `E:\SchoolContents\智能创造\小组实验\AI技术-实验4.1-实验要求-医学图像技术调研`
- **我的角色**: 负责**提示词方式（方式1）**，不负责Skill方式

## 准备工作
- 读取实验要求文档
- 探索论文文件夹（4类28篇：SAM相关9篇、眼底病变分割9篇、医学图像增强5篇、SAM蒸馏6篇）
- 安装25个Skills（deep-research、nature-writing、nature-paper2ppt、docx、pptx等）
- 创建文件夹 `PromptV/` 和 `SkillV/`

## 提示词方式执行过程（4轮）

### 第①轮 — SOTA调研
- **提示词**: `PromptV/prompt1_sota.md` — 按4类论文分类整理，供Gemini理解
- **回复**: `PromptV/response_round1.md` — SOTA方法、数据集、评估指标、性能对比表
- ✅

### 第②轮 — 问题分析
- **提示词**: `PromptV/prompt2_problems.md` — a)迁移适配 b)图像质量 c)跨领域迁移
- **回复**: `PromptV/response_round2.md` — 4大问题分析+问题-解决方案对照表
- ✅

### 第③轮 — 实验蓝图
- **提示词**: `PromptV/prompt3_experiment.md` — Baseline选择、架构详解、改进方案、实验配置
- **回复**: `PromptV/response_round3.md` — Baseline:SAM-Adapter+MedSAM, 3个改进模块(增强先验/形变Adapter/自动Prompt), IDRiD数据集
- ✅

### 第④轮 — 生成报告
- **提示词**: `PromptV/prompt4_report.md` — 合并格式规范，要求3000-5000字，纯黑宋体标准论文格式
- **回复**: `PromptV/response_round4_report.md` → 转为Word文档
- **最终报告**: `PromptV/AI技术-实验4.1-医学图像技术调研报告.docx`（11460字，2个表格，10篇参考文献，5章结构a→b→d→e→f）
- ✅

### 格式修正
- 补充格式修正提示词 `prompt_format_fix.md`（后合并入prompt4_report.md）
- 修正了章节编号（c→d），去除了多余章节（g实验总结），强调了字体颜色规范

## 实验任务分工确认
- **提示词方式（方式1）**: 全部完成 ✅
- **Skill方式（方式2）**: 不由我负责
- **实验要求1) 环境配置**: 用户自行记录
- **实验要求2) Agent轨迹+Skill记录**: Skill方式完成后做
- **实验要求3) 实验PPT**: Skill方式完成后做
- **实验要求4) 心得体会**: 全部完成后做

## 最终文件结构
```
PromptV/
├── prompt1_sota.md              # 第①轮提示词
├── response_round1.md           # 第①轮回复
├── prompt2_problems.md          # 第②轮提示词
├── response_round2.md           # 第②轮回复
├── prompt3_experiment.md        # 第③轮提示词
├── response_round3.md           # 第③轮回复
├── prompt4_report.md            # 第④轮提示词（含格式规范）
├── AI技术-实验4.1-医学图像技术调研报告.docx  # 最终报告
SkillV/                          # 空（Skill方式产出）
PChat.md                         # 本文件
Plan.md                          # 执行计划
```

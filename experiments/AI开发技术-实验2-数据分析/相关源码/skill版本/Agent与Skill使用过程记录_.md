# Agent与Skill使用过程记录（Skill增强版本）

> 项目：就业状态分析与预测  
> 实验方式：Skill增强版本  
> AI工具：Claude Code (Claude Opus 4.7) + VS Code 插件扩展  
> 记录时间：2026-05-18

---

## 1. 本次使用的Skill总览

| Skill名称 | 使用阶段 | 调用次数 | 核心作用 |
|-----------|---------|---------|---------|
| **data-analyst-prompter** | 数据预处理 | 1次 | EDA优先方法、Schema注入、假设验证框架 |
| **math-modeling** | 问题一~四 | 多次 | 建模三阶段指导（分析→代码→论文） |
| **simplify** | 数据预处理后 | 1次 | 三Agent并行审查（复用/质量/效率） |
| **research-writing** | 报告撰写 | 1次 | 30个Prompt模板指导论文写作流程 |
| **pdf** | 开始时 | 1次 | 提取加密范例报告（复用Prompt版已解密的） |

---

## 2. 各阶段Skill使用详情

### 2.1 数据预处理 — data-analyst-prompter

**调用方式**：`Skill("data-analyst-prompter")`

**技能提供的方法论**：
- **强制代码执行模式**：不允许AI直接回答数字，必须写Python代码计算
- **Schema注入**：在分析前完整定义54个字段的Schema（类型、含义、取值）
- **EDA优先原则**：5项结构化检查（数据类型→空值分布→基本统计→关键字段→预测集验证）
- **假设-验证框架**：标签构建从简单if-else改为5假设(H1-H5)框架化验证

**与Prompt版的关键差异**：
- Prompt版：临时探索脚本，无结构化流程
- Skill版：Phase 0-6六阶段清晰输出，每阶段有明确方法论标签

### 2.2 数据预处理后 — simplify代码审查

**调用方式**：`Skill("simplify")` → 自动启动三Agent并行审查

**三Agent审查结果**：

| Agent | 发现的问题 | 是否修复 |
|-------|-----------|---------|
| 复用审查 | clean_null()可用df.replace替代、众数填充逻辑重复 | ✅ 已修复 |
| 质量审查 | hukou_label的float→str Bug导致全部NaN | ✅ 已修复(int键) |
| 效率审查 | 逐行apply→向量化np.select、重复read_excel | ✅ 已修复 |

**Bug发现价值**：质量审查Agent发现`c_aac009`被`pd.to_numeric`转为float后`.astype(str)`产生`"10.0"`→与字典key`"10"`不匹配，导致`hukou_label`全部为NaN。这个Bug在Prompt版中未被发现。

### 2.3 问题一 — math-modeling + data-analyst-prompter

**调用方式**：`Skill("math-modeling")`

**技能指导的改进**：
- 从单纯的描述性统计升级为**统计推断**：卡方独立性检验 + Cramér's V效应量 + Spearman秩相关
- 遵循"建模分析→代码实现→论文撰写"三阶段流程
- 参考了技能资源库中的统计分析与数据处理算法说明

**关键产出**：
- 统计检验汇总表（6个特征的χ²、p值、显著性、Cramér's V）
- 双相关系数验证（Pearson + Spearman）
- 发现仅户口性质显著（p<0.001），其余特征均不显著

### 2.4 问题二~四 — math-modeling持续指导

**问题二改进（class_weight + 5折CV + GridSearchCV）**：
- 5折分层CV替代单次划分
- 所有模型启用类别平衡机制
- 新增ROC-AUC评估指标
- 报告均值±标准差

**问题三改进（个体-宏观交互特征）**：
- 4个交互特征：age×GDP、age×失业率、edu×招聘指数、hukou×第三产业
- 严格CV对比（同一划分、不同特征集）

**问题四改进（岗位聚合 + 加权 + 多样性）**：
- 3846个体→63个行业×区域岗位类型
- 12维加权特征（教育/技能1.5×）
- Top-3多样性约束（强制不同行业）

### 2.5 报告撰写 — research-writing

**调用方式**：`Skill("research-writing")`

**实际使用的模板**：
- 摘要写作模板（#23）：4段式结构
- 实验结果分析模板（#15）：段落式自然陈述
- 大纲生成模板（#21）：章节结构设计

---

## 3. Agent使用情况

与Prompt版不同，Skill版**主动使用了simplify的并行Agent审查**：

| Agent类型 | 用途 | 效果 |
|----------|------|------|
| 代码复用审查Agent | 检查预处理脚本的重复逻辑 | 发现2处可复用代码 |
| 代码质量审查Agent | 检查Bug和代码坏味道 | **发现hukou_label关键Bug** |
| 效率审查Agent | 检查性能问题 | 发现6处可向量化优化 |
| 修复Agent | 自动应用三Agent的修复建议 | 6项优化成功应用 |

三个审查Agent在**同一消息中并行启动**，约50秒内全部完成。这是Skill版本相比Prompt版本在工程效率上的一个显著优势。

---

## 4. Skill版本与Prompt版本的工作流对比

| 维度 | Prompt版 | Skill增强版 |
|------|---------|------------|
| **启动方式** | 直接对话"先做数据探索" | Skill调用→方法论注入→再执行 |
| **EDA** | 临时探索脚本 | data-analyst-prompter 5步结构化检查 |
| **标签构建** | 4条if-else | 5假设(H1-H5)验证框架 |
| **代码质量** | 无审查 | simplify三Agent并行审查+自动修复 |
| **建模** | 直接写代码 | math-modeling三阶段流程 |
| **统计检验** | 无 | 卡方+Cramér's V+Spearman |
| **模型评估** | 单次split | 5折CV+GridSearchCV |
| **类别平衡** | 未处理 | class_weight+scale_pos_weight |
| **报告** | 直接写LaTeX | research-writing模板指导 |

---

## 5. Skill调用时机总结

```
项目开始
  ├─ pdf Skill ─────────── 提取加密范例报告
  │
数据预处理
  ├─ data-analyst-prompter ─ EDA优先+Schema注入
  ├─ simplify ───────────── 三Agent审查+自动修复
  │
问题一
  ├─ math-modeling ──────── 建模分析→统计检验指导
  │
问题二~四
  ├─ math-modeling ──────── 持续建模指导
  │
报告
  └─ research-writing ───── 论文写作模板
```

---

## 6. 问题与反思

### Skill版本的优势
- **方法论驱动**：每个阶段有明确的Skill指导框架，不再是"想到哪做到哪"
- **Bug发现自动化**：simplify的质量审查Agent发现了人工审查容易遗漏的类型转换Bug
- **统计严谨性**：从描述统计升级到统计推断（卡方检验+p值+效应量）
- **评估可靠性**：CV替代单次划分，标准差量化不确定性

### 仍存在的局限
- **数据信号弱**：统计检验显示个人特征与就业状态关联极弱（V<0.07），模型精度受数据本身限制
- **宏观数据为模拟值**：基于公开统计趋势推定，非真实宜昌月度数据
- **匹配区分度**：虽然从0.998降到0.944，但理想值应在0.7-0.85区间
- **部分Skill未充分使用**：research-writing有30个模板，实际只用了3个

---

*记录完成时间：2026-05-18*

# 自定义Skill创建过程

> 项目：AI开发技术-实验2  
> 实验目的第4点：自动生成Skill，并进一步改进Skill  
> 时间：2026-05-18

---

## 一、为什么要创建自定义Skill

在完成Prompt版本和Skill增强版本的对比实验后，我们发现：

- **现有Skill各自独立**，缺少一个协调者来确保"数据分析→建模→论文"全流程的质量
- **LaTeX专项支持缺失**，所有写作类Skill面向通用/docx场景
- **数据科学常见硬伤**（类别不平衡、CV缺失、特征重要性来源错误）没有Skill主动检查

于是我们基于实战踩坑经验，设计了2个自定义Skill。

---

## 二、Skill的文件结构规范

每个Skill是一个独立的文件夹，存放在以下路径之一：

| 路径 | 作用域 |
|------|--------|
| `~/.claude/skills/[skill名]/` | 全局生效，所有项目可用 |
| `.claude/skills/[skill名]/` | 项目级别，仅当前项目可用 |

本项目的自定义Skill存放在项目级别路径：

```
.claude/skills/
├── data-modeling-pipeline/
│   └── SKILL.md
└── latex-report-generator/
    └── SKILL.md
```

### SKILL.md 格式要求

```markdown
---
name: skill-name
description: 一句话描述——包含触发关键词和使用场景
---

# Skill标题

Skill的完整内容（Markdown格式）：
- 角色设定
- 方法论
- 约束规则
- 检查清单
- 输出格式要求
```

**关键点**：
- `name`：用于 `Skill(skill="name")` 调用
- `description`：用于系统自动判断何时加载，必须包含触发关键词
- 正文：给AI的角色设定、方法论指导、约束规则

---

## 三、自定义Skill 1：data-modeling-pipeline

### 3.1 设计背景

**实战中的观察**：

在Prompt版本中，我们发现AI会犯以下错误：
- 类别不平衡不处理 → 失业召回率≈0
- 单次train_test_split → 结果不稳定
- KNN没有feature_importances_ → 拿来取特征重要性（全部等值）
- hukou_label的float→str类型转换Bug无人发现

在Skill增强版本中，虽然使用了data-analyst-prompter和math-modeling，但它们各自独立工作，没有人在阶段之间做质量检查。

**设计思路**：创建一个"门禁协调器"，在数据分析全流程的4个关键节点设置强制检查点。

### 3.2 Skill内容结构

```
data-modeling-pipeline/SKILL.md
├── 核心理念：阶段门禁 (Stage Gate)
├── 门禁1：数据预处理质量检查
│   ├── Schema完整性
│   ├── 缺失值分层处理
│   ├── 标签构建验证
│   └── 中文数据专项（\N处理、类型转换验证）
├── 门禁2：统计验证（建模前必做）
│   ├── 卡方检验代码模板
│   ├── Cramér's V效应量
│   ├── Pearson+Spearman双验证
│   └── 检查标准清单
├── 门禁3：建模规范检查
│   ├── 类别不平衡处理（必须）
│   ├── 评估方法（禁止单次split）
│   ├── 超参数调优（推荐GridSearchCV）
│   └── 特征重要性来源验证（禁止从KNN/SVM取）
├── 门禁4：报告完整性检查
│   ├── 必须包含的章节
│   ├── 图表规范
│   └── 数据科学报告专项（统计检验表、CV结果、混淆矩阵）
├── 全流程执行顺序
└── 7个常见错误速查表
```

### 3.3 设计原则

| 原则 | 说明 | 例子 |
|------|------|------|
| **基于实战踩坑** | 每个规则来自实际遇到的问题 | float→str→map的Bug |
| **硬性约束优先** | 该强制的地方不委婉 | "禁止单次split"而非"建议使用CV" |
| **检查清单形式** | 让AI逐项核对 | 4个门禁各有checkbox |
| **中文场景适配** | 针对中文数据特点 | \N空值标记、中文字体 |
| **最小可行** | 先覆盖最高频问题 | 7个常见错误 > 100个罕见错误 |

### 3.4 触发关键词

`数学建模` `数据分析全流程` `建模流程` `数据科学pipeline` `端到端建模` `建模质量检查` `就业预测` `分类建模` `数据挖掘项目`

---

## 四、自定义Skill 2：latex-report-generator

### 4.1 设计背景

**实战中的观察**：

在Prompt版本中，LaTeX编译遇到了：
- 字体文件缺失 → 100+编译错误
- 代码附录5个完整文件（300+行）→ PDF从30页溢出到79页，内容重复
- 封面只有一行居中标题 → 缺少完整封面页

在Skill增强版本中：
- research-writing有30个模板，但全部面向通用/docx场景
- 没有一个模板教AI如何正确使用cumcmthesis模板

**设计思路**：创建一个专门针对cumcmthesis模板的LaTeX报告生成Skill，把踩过的坑固化为检查规则。

### 4.2 Skill内容结构

```
latex-report-generator/SKILL.md
├── cumcmthesis模板速查
│   ├── 文档类选项（withoutpreface/bwprint）
│   ├── 必须的元信息（title/tihao等）
│   └── 字体配置
├── 封面与目录
│   ├── 自定义封面（titlepage环境）
│   └── 目录（需编译2次）
├── 图表管理
│   ├── 单图/双图并列模板
│   └── 图表路径管理规范
├── 表格规范（三线表/宽表格）
├── 代码附录（关键！）
│   ├── 核心原则：只放关键代码段
│   ├── firstline/lastline行号控制
│   └── 代码段选取原则（每段20-40行）
├── 编译流程（xelatex→bibtex→xelatex→xelatex）
├── 5个常见编译问题速查表
├── 报告结构模板（11个章节）
└── 制作报告的标准步骤（6步）
```

### 4.3 设计亮点

**代码附录长度控制**——这是最关键的规则：

错误做法（导致PDF溢出）：
```latex
\lstinputlisting[language=python]{code/full_script.py}  % 300行
```

正确做法：
```latex
\lstinputlisting[language=python,firstline=96,lastline=158]{code/q1.py}  % 62行
```

这条规则直接来自Prompt版报告的翻车经历（79页→30页的修复）。

### 4.4 触发关键词

`LaTeX报告` `数模论文` `cumcmthesis` `XeLaTeX编译` `技术报告模板` `数学建模论文LaTeX` `生成PDF报告`

---

## 五、创建过程总结

### 5.1 创建流程

```
观察实战问题 → 分析现有Skill不足 → 设计新Skill
    │                  │                    │
    ▼                  ▼                    ▼
7个踩坑记录      4个Skill的不足点      2个新Skill
                - 各自独立            - data-modeling-pipeline
                - LaTeX缺失           - latex-report-generator
                - 硬伤检测缺失
```

### 5.2 关键设计决策

| 决策 | 原因 |
|------|------|
| 创建2个独立Skill而非1个综合Skill | 用户要求做多个独立Skill，效果更好 |
| 项目级别(.claude/skills/)而非全局(~/.claude/skills/) | 仅当前项目需要，避免污染全局环境 |
| 简单结构(SKILL.md单文件)而非复杂结构(assets/references/tools) | 最小可行，后续按需扩展 |
| 硬性约束 > 软性建议 | 来自Prompt版的教训：AI需要明确禁止，而非委婉提醒 |

### 5.3 与实验目的的对应

| 实验目的 | 本环节的体现 |
|---------|------------|
| 了解数据分析的流程 | 门禁1覆盖数据预处理全流程 |
| 掌握大模型进行数据分析 | 门禁2-3指导建模和评估 |
| 了解Agent和Skills技术 | 2个自定义Skill的完整设计和实现 |
| 自动生成并改进Skill | 基于实战观察→设计→实现→文档化 |

### 5.4 后续改进方向

1. 为data-modeling-pipeline添加更多错误速查条目（从后续项目中积累）
2. 为latex-report-generator添加更多LaTeX模板变体（如beamer幻灯片）
3. 考虑添加assets/子目录存放代码模板
4. 考虑添加references/子目录存放示例报告

---

## 六、Skill文件清单

| 文件 | 路径 | 大小 | 说明 |
|------|------|------|------|
| SKILL.md | `.claude/skills/data-modeling-pipeline/` | ~3KB | 全流程门禁协调器 |
| SKILL.md | `.claude/skills/latex-report-generator/` | ~3KB | LaTeX报告生成器 |

两个Skill已自动加载，可在Claude Code中通过 `Skill(skill="data-modeling-pipeline")` 或 `Skill(skill="latex-report-generator")` 调用。

---

*文档完成时间：2026-05-18*
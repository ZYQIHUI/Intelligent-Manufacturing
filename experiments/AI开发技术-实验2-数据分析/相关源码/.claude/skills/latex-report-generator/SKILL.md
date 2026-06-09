---
name: latex-report-generator
description: LaTeX数学建模报告生成器——cumcmthesis模板专项支持、图表管理、代码附录控制、常见编译问题速查。Use when user mentions: LaTeX报告, 数模论文, cumcmthesis, XeLaTeX编译, 技术报告模板, 数学建模论文LaTeX, 生成PDF报告
---

# LaTeX数学建模报告生成器 - LaTeX Report Generator

你是cumcmthesis模板的LaTeX报告生成专家。核心职责是帮助用户从代码和图表快速生成高质量的中文数学建模技术报告PDF。

---

## 一、cumcmthesis模板速查

### 1.1 文档类选项
```latex
\documentclass[withoutpreface,bwprint]{cumcmthesis}
% withoutpreface: 跳过承诺书/编号页（非正式竞赛用）
% bwprint: 黑白打印模式
```

### 1.2 必须的元信息
```latex
\title{论文标题}
\tihao{题号}        % 如 C
\baominghao{}       % 报名号（可空）
\schoolname{}       % 学校（可空）
```

### 1.3 字体配置
- 中文：SimHei/Microsoft YaHei（`\usepackage{ctex}` 自动处理）
- 等宽字体（代码）：需提供 YaHei.Consolas.ttf + Fira Code.otf 到编译目录
- 字体警告可忽略，不影响输出

---

## 二、封面与目录

### 2.1 自定义封面（推荐用于非竞赛报告）
```latex
\begin{titlepage}
\thispagestyle{empty}
\vspace*{3cm}
\begin{center}
{\zihao{1}\bfseries\songti 论文标题\\[12pt]}
{\zihao{3}\kaishu 副标题\\[36pt]}
{\zihao{4}\songti 关键词：xxx~~xxx~~xxx}
\vfill
{\zihao{4}\songti 日期}
\end{center}
\end{titlepage}
```

### 2.2 目录
```latex
\tableofcontents
\newpage
```
- XeLaTeX需编译2次才能正确生成目录和交叉引用

---

## 三、图表管理

### 3.1 单图
```latex
\begin{figure}[ht]
\centering
\includegraphics[width=0.85\textwidth]{figures/01_chart.png}
\caption{图表标题}
\label{fig:xxx}
\end{figure}
```

### 3.2 双图并列
```latex
\begin{figure}[ht]
\centering
\subcaptionbox{左图标题\label{fig:left}}
{\includegraphics[width=0.48\textwidth]{figures/left.png}}
\subcaptionbox{右图标题\label{fig:right}}
{\includegraphics[width=0.48\textwidth]{figures/right.png}}
\caption{总标题}
\end{figure}
```
- 需 `\usepackage{subcaption}`

### 3.3 图表路径管理
- 所有图表统一放在 `figures/` 子目录
- 命名规范：`[序号]_[内容].png`（如 `01_employment_overview.png`）
- 编译前确保所有引用图片存在，否则编译报错

---

## 四、表格规范

### 4.1 标准三线表
```latex
\begin{table}[H]
\centering
\caption{表格标题}
\begin{tabular}{lccc}
\toprule
列1 & 列2 & 列3 & 列4 \\
\midrule
数据 & 数据 & 数据 & 数据 \\
\bottomrule
\end{tabular}
\label{tab:xxx}
\end{table}
```
- 需 `\usepackage{booktabs}`

### 4.2 宽表格
```latex
\begin{tabularx}{\textwidth}{CCCC}  % C列自动居中等宽
```

---

## 五、代码附录（关键！）

### 5.1 核心原则：只放关键代码段，不放完整文件

**错误做法**（导致PDF溢出/重复）：
```latex
\lstinputlisting[language=python]{code/full_script.py}  % 300行完整代码
```

**正确做法**：
```latex
\lstinputlisting[language=python,firstline=96,lastline=158]{code/q1.py}
% 只展示关键函数/逻辑段，60行以内为佳
```

### 5.2 代码段选取原则
- 数据预处理：标签构建逻辑（20-40行）
- 问题一：统计检验核心代码（30行）
- 问题二：模型训练与CV评估（40行）
- 问题三：交互特征构建（25行）
- 问题四：匹配算法核心（40行）

---

## 六、编译流程

```bash
# 1. 首次编译（生成aux/toc）
xelatex -interaction=nonstopmode report.tex

# 2. 参考文献
bibtex report

# 3. 第二次编译（更新交叉引用）
xelatex -interaction=nonstopmode report.tex

# 4. 第三次编译（最终确认引用）
xelatex -interaction=nonstopmode report.tex
```

---

## 七、常见编译问题速查

| 问题 | 错误信息 | 解决方案 |
|------|---------|---------|
| 缺字体 | Cannot use \XeTeXOTfeaturetag with nullfont | 复制.ttf/.otf字体文件到编译目录 |
| 图片不存在 | File not found: figures/xxx.png | 检查路径，确认为PNG格式 |
| 引用未定义 | undefined references | 再编译一次XeLaTeX |
| 代码附录超长 | PDF页面溢出/内容重复 | 使用firstline/lastline限制行数 |
| 中文乱码 | 显示为方块 | 确认\setCJKmainfont字体已安装 |
| 表格太宽 | Overfull hbox | 改用tabularx |

---

## 八、报告结构模板

```latex
封面页(titlepage)
目录(\tableofcontents)
摘要(abstract + keywords)
一、问题重述（背景 + 要求）
二、问题分析（每题一段）
三、模型假设（列表）
四、符号说明（表格）
五~八、问题一~四（模型建立→求解→结果）
九、模型分析与检验
十、模型评价（优点+缺点）
参考文献
附录（文件列表 + 核心代码段）
```

---

## 九、制作报告的标准步骤

1. 确认所有图表已生成并存放到 `figures/`
2. 确认代码文件已复制到 `code/`（选取关键段的行号范围）
3. 复制模板文件（.cls, .bst, .bib, 字体.ttf/.otf）到报告目录
4. 按上方"报告结构模板"撰写 .tex 文件
5. 执行编译流程（xelatex→bibtex→xelatex→xelatex）
6. 检查PDF：封面→目录→图表位置→引用正确→附录代码不溢出

---

## 十、使用方式

当用户要求生成LaTeX报告时：
1. 先扫描项目中的所有图表文件和代码文件
2. 建议封面信息和报告结构
3. 在写.tex前确认图表路径和代码行号范围
4. 编译后检查常见问题（字体/引用/溢出）
5. 根据用户反馈修复

**记住：代码附录只放关键段，不要全文粘贴。这是最常见的翻车点。**
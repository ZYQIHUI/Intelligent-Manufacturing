"""
问题一：数据特征分析
就业状态多维度分析 + 可视化
"""
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import seaborn as sns
import os
import warnings
warnings.filterwarnings("ignore")

# ============================================================
# 0. 初始化
# ============================================================
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CHART_DIR = os.path.join(SCRIPT_DIR, "charts")
os.makedirs(CHART_DIR, exist_ok=True)

# 中文字体设置
plt.rcParams["font.sans-serif"] = ["SimHei", "Microsoft YaHei", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False

# 加载数据
DATA_PATH = os.path.join(SCRIPT_DIR, "..", "数据预处理", "train_clean.csv")
df = pd.read_csv(DATA_PATH)
print(f"加载数据: {len(df)} 条")

COLOR_PALETTE = ["#4472C4", "#ED7D31", "#A5A5A5", "#FFC000", "#5B9BD5"]


def save_chart(filename, dpi=150):
    """保存图表到charts目录"""
    path = os.path.join(CHART_DIR, filename)
    plt.savefig(path, dpi=dpi, bbox_inches="tight", facecolor="white")
    print(f"  已保存: {filename}")


# ============================================================
# Step 1: 就业状态总览
# ============================================================
print("\n" + "=" * 60)
print("Step 1: 就业状态总览")
print("=" * 60)

emp = (df["employment_status"] == 1).sum()
unemp = (df["employment_status"] == 0).sum()
print(f"就业: {emp} ({emp/len(df)*100:.1f}%)")
print(f"失业: {unemp} ({unemp/len(df)*100:.1f}%)")

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

# 饼图
colors = ["#4472C4", "#ED7D31"]
ax1.pie([emp, unemp], labels=["就业", "失业"], autopct="%1.1f%%",
        colors=colors, explode=(0, 0.05), shadow=True, startangle=90,
        textprops={"fontsize": 13})
ax1.set_title("当前就业状态分布", fontsize=15, fontweight="bold")

# 柱状图
bars = ax2.bar(["就业", "失业"], [emp, unemp], color=colors, edgecolor="white", width=0.5)
for bar, val in zip(bars, [emp, unemp]):
    ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 30,
             f"{val}\n({val/len(df)*100:.1f}%)", ha="center", fontsize=13, fontweight="bold")
ax2.set_ylabel("人数", fontsize=12)
ax2.set_title("就业状态数量统计", fontsize=15, fontweight="bold")
ax2.set_ylim(0, max(emp, unemp) * 1.15)

plt.tight_layout()
save_chart("01_employment_overview.png")
plt.close()

# ============================================================
# Step 2: 年龄维度
# ============================================================
print("\nStep 2: 年龄维度分析")

fig, axes = plt.subplots(1, 3, figsize=(18, 5))

# 年龄分布直方图
ax = axes[0]
ax.hist(df["age"], bins=30, color=COLOR_PALETTE[0], edgecolor="white", alpha=0.85)
ax.axvline(df["age"].mean(), color="red", linestyle="--", linewidth=2, label=f"均值={df['age'].mean():.1f}岁")
ax.axvline(df["age"].median(), color="orange", linestyle="--", linewidth=2, label=f"中位数={df['age'].median():.0f}岁")
ax.set_xlabel("年龄", fontsize=11)
ax.set_ylabel("人数", fontsize=11)
ax.set_title("年龄分布", fontsize=13, fontweight="bold")
ax.legend(fontsize=9)

# 各年龄段就业率
ax = axes[1]
age_order = ["16-25岁", "26-35岁", "36-45岁", "46-55岁", "56岁以上"]
age_groups = df.groupby("age_group", observed=False)
age_emp_rate = (age_groups["employment_status"].mean() * 100).reindex(age_order)
age_counts = age_groups.size().reindex(age_order)

bars = ax.bar(range(len(age_order)), age_emp_rate.values, color=COLOR_PALETTE[:5], edgecolor="white")
for i, (bar, rate, count) in enumerate(zip(bars, age_emp_rate.values, age_counts.values)):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
            f"{rate:.1f}%\n(n={count})", ha="center", fontsize=9)
ax.set_xticks(range(len(age_order)))
ax.set_xticklabels(age_order, fontsize=10)
ax.set_ylabel("就业率 (%)", fontsize=11)
ax.set_title("各年龄段就业率", fontsize=13, fontweight="bold")
ax.set_ylim(0, 100)

# 年龄×性别交叉
ax = axes[2]
for sex_val, sex_label, color in [(1, "男", "#4472C4"), (2, "女", "#ED7D31")]:
    subset = df[df["sex"] == sex_val]
    rates = subset.groupby("age_group", observed=False)["employment_status"].mean() * 100
    rates = rates.reindex(age_order)
    ax.plot(range(len(age_order)), rates.values, marker="o", linewidth=2,
            markersize=8, label=sex_label, color=color)
ax.set_xticks(range(len(age_order)))
ax.set_xticklabels(age_order, fontsize=10)
ax.set_ylabel("就业率 (%)", fontsize=11)
ax.set_title("年龄×性别交叉就业率", fontsize=13, fontweight="bold")
ax.set_ylim(0, 100)
ax.legend(fontsize=10)

plt.tight_layout()
save_chart("02_age_analysis.png")
plt.close()

# ============================================================
# Step 3: 性别维度
# ============================================================
print("Step 3: 性别维度分析")

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

# 男女就业/失业人数堆叠
sex_data = df.groupby("sex_label")["employment_status"].value_counts().unstack()
sex_data.columns = ["失业", "就业"]
sex_data = sex_data.reindex(["男", "女"])

sex_data.plot(kind="bar", stacked=True, ax=ax1, color=[COLOR_PALETTE[1], COLOR_PALETTE[0]], edgecolor="white")
for i, (idx, row) in enumerate(sex_data.iterrows()):
    total = row.sum()
    ax1.text(i, total + 30, f"总计={total}", ha="center", fontsize=11, fontweight="bold")
    ax1.text(i, row["就业"]/2, f"{row['就业']}", ha="center", fontsize=10, color="white")
    ax1.text(i, row["就业"] + row["失业"]/2, f"{row['失业']}", ha="center", fontsize=10)
ax1.set_xlabel("性别", fontsize=11)
ax1.set_ylabel("人数", fontsize=11)
ax1.set_title("不同性别就业状态分布", fontsize=13, fontweight="bold")
ax1.legend(loc="upper right")

# 男女就业率对比
male_rate = df[df["sex"] == 1]["employment_status"].mean() * 100
female_rate = df[df["sex"] == 2]["employment_status"].mean() * 100

bars = ax2.bar(["男", "女"], [male_rate, female_rate], color=COLOR_PALETTE[:2], edgecolor="white", width=0.4)
for bar, rate in zip(bars, [male_rate, female_rate]):
    ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
             f"{rate:.1f}%", ha="center", fontsize=14, fontweight="bold")
ax2.set_ylabel("就业率 (%)", fontsize=11)
ax2.set_title("不同性别就业率对比", fontsize=13, fontweight="bold")
ax2.set_ylim(0, 100)

plt.tight_layout()
save_chart("03_gender_analysis.png")
plt.close()

# ============================================================
# Step 4: 学历维度
# ============================================================
print("Step 4: 学历维度分析")

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

# 学历就业/失业分布
edu_order = ["初中及以下", "中专/高中", "专科/本科及以上"]
edu_data = df.groupby("edu_label")["employment_status"].value_counts().unstack()
edu_data.columns = ["失业", "就业"]
edu_data = edu_data.reindex(edu_order)

edu_data.plot(kind="bar", stacked=True, ax=ax1, color=[COLOR_PALETTE[1], COLOR_PALETTE[0]], edgecolor="white")
for i, (idx, row) in enumerate(edu_data.iterrows()):
    total = row.sum()
    ax1.text(i, total + 20, f"n={total}", ha="center", fontsize=10, fontweight="bold")
ax1.set_xlabel("学历", fontsize=11)
ax1.set_ylabel("人数", fontsize=11)
ax1.set_title("不同学历就业状态分布", fontsize=13, fontweight="bold")
ax1.legend()

# 学历就业率
edu_rates = (df.groupby("edu_label")["employment_status"].mean() * 100).reindex(edu_order)
bars = ax2.bar(range(len(edu_order)), edu_rates.values, color=COLOR_PALETTE[:3], edgecolor="white")
for i, (bar, rate) in enumerate(zip(bars, edu_rates.values)):
    ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
             f"{rate:.1f}%", ha="center", fontsize=14, fontweight="bold")
ax2.set_xticks(range(len(edu_order)))
ax2.set_xticklabels(edu_order, fontsize=10)
ax2.set_ylabel("就业率 (%)", fontsize=11)
ax2.set_title("不同学历就业率对比", fontsize=13, fontweight="bold")
ax2.set_ylim(0, 100)

plt.tight_layout()
save_chart("04_education_analysis.png")
plt.close()

# ============================================================
# Step 5: 行业维度
# ============================================================
print("Step 5: 行业维度分析")

# 行业大类映射
industry_map = {
    "A": "农/林/牧/渔", "B": "采矿", "C": "制造", "D": "电力/热力",
    "E": "建筑", "F": "批发/零售", "G": "交通运输", "H": "住宿/餐饮",
    "I": "信息技术", "J": "金融", "K": "房地产", "L": "租赁/商务服务",
    "M": "科研/技术服务", "N": "水利/环境", "O": "居民服务", "P": "教育",
    "Q": "卫生/社会工作", "R": "文化/体育/娱乐", "S": "公共管理/社会保障",
    "Z": "其他"
}
df["industry_name"] = df["industry_category"].map(industry_map)

# Top15行业就业人数
industry_emp = df[df["employment_status"] == 1]["industry_name"].value_counts().head(15)
industry_unemp = df[df["employment_status"] == 0]["industry_name"].value_counts().head(15)

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))

# 就业人数最多的行业Top15
colors_emp = [COLOR_PALETTE[0]] * 15
bars = ax1.barh(range(len(industry_emp)), industry_emp.values, color=colors_emp, edgecolor="white")
ax1.set_yticks(range(len(industry_emp)))
ax1.set_yticklabels(industry_emp.index, fontsize=9)
ax1.set_xlabel("就业人数", fontsize=11)
ax1.set_title("就业人数最多的行业 (Top15)", fontsize=13, fontweight="bold")
ax1.invert_yaxis()
for bar, val in zip(bars, industry_emp.values):
    ax1.text(bar.get_width() + 3, bar.get_y() + bar.get_height()/2, str(val), va="center", fontsize=9)

# 各行业就业率 (样本量>=30)
industry_stats = df.groupby("industry_name").agg(
    总人数=("employment_status", "count"),
    就业率=("employment_status", "mean")
).query("总人数 >= 30").sort_values("就业率", ascending=True)

bars = ax2.barh(range(len(industry_stats)), industry_stats["就业率"].values * 100,
                color=COLOR_PALETTE[:len(industry_stats)], edgecolor="white")
ax2.set_yticks(range(len(industry_stats)))
ax2.set_yticklabels(industry_stats.index, fontsize=9)
ax2.set_xlabel("就业率 (%)", fontsize=11)
ax2.set_title("各行业就业率 (样本≥30)", fontsize=13, fontweight="bold")
for bar, rate in zip(bars, industry_stats["就业率"].values * 100):
    ax2.text(bar.get_width() + 0.5, bar.get_y() + bar.get_height()/2, f"{rate:.1f}%", va="center", fontsize=9)

plt.tight_layout()
save_chart("05_industry_analysis.png")
plt.close()

# ============================================================
# Step 6: 婚姻与户口维度
# ============================================================
print("Step 6: 婚姻与户口维度")

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

# 婚姻状态
marriage_order = ["未婚", "已婚", "离婚", "丧偶"]
marriage_rates = (df.groupby("marriage_label")["employment_status"].mean() * 100).reindex(marriage_order)
marriage_counts = df.groupby("marriage_label").size().reindex(marriage_order)

bars = ax1.bar(range(len(marriage_order)), marriage_rates.values, color=COLOR_PALETTE[:4], edgecolor="white")
for i, (bar, rate, count) in enumerate(zip(bars, marriage_rates.values, marriage_counts.values)):
    ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
             f"{rate:.1f}%\n(n={count})", ha="center", fontsize=10)
ax1.set_xticks(range(len(marriage_order)))
ax1.set_xticklabels(marriage_order, fontsize=10)
ax1.set_ylabel("就业率 (%)", fontsize=11)
ax1.set_title("不同婚姻状态就业率", fontsize=13, fontweight="bold")
ax1.set_ylim(0, 100)

# 户口性质
hukou_order = ["农业", "非农业", "统一居民户口"]
hukou_rates = (df.groupby("hukou_label")["employment_status"].mean() * 100).reindex(hukou_order)
hukou_counts = df.groupby("hukou_label").size().reindex(hukou_order)

bars = ax2.bar(range(len(hukou_order)), hukou_rates.values, color=COLOR_PALETTE[:3], edgecolor="white")
for i, (bar, rate, count) in enumerate(zip(bars, hukou_rates.values, hukou_counts.values)):
    ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
             f"{rate:.1f}%\n(n={count})", ha="center", fontsize=10)
ax2.set_xticks(range(len(hukou_order)))
ax2.set_xticklabels(hukou_order, fontsize=10)
ax2.set_ylabel("就业率 (%)", fontsize=11)
ax2.set_title("不同户口性质就业率", fontsize=13, fontweight="bold")
ax2.set_ylim(0, 100)

plt.tight_layout()
save_chart("06_marriage_hukou.png")
plt.close()

# ============================================================
# Step 7: 特征相关性
# ============================================================
print("Step 7: 特征相关性分析")

# 选取数值型特征和可编码特征
corr_features = [
    "employment_status", "age", "sex", "nation", "marriage", "edu_level",
    "politic", "religion", "c_aac009", "c_aac011", "type",
    "military_status", "is_disability", "is_teen", "is_elder",
    "change_type", "is_living_alone"
]
# 确保特征在df中存在且转为数值
corr_df = df[corr_features].copy()
for col in corr_df.columns:
    corr_df[col] = pd.to_numeric(corr_df[col], errors="coerce")
corr_df = corr_df.dropna()

corr_matrix = corr_df.corr()

fig, ax = plt.subplots(figsize=(12, 10))
mask = np.triu(np.ones_like(corr_matrix, dtype=bool))
sns.heatmap(corr_matrix, mask=mask, annot=True, fmt=".2f", cmap="RdBu_r",
            center=0, square=True, linewidths=0.5, ax=ax,
            annot_kws={"fontsize": 7}, cbar_kws={"shrink": 0.8})
ax.set_title("各特征与就业状态的相关性热力图", fontsize=14, fontweight="bold")

plt.tight_layout()
save_chart("07_correlation_heatmap.png")
plt.close()

# 打印特征与就业状态的相关系数排序
corr_with_target = corr_matrix["employment_status"].drop("employment_status").sort_values(key=abs, ascending=False)
print("\n特征与就业状态相关系数 (绝对值排序Top10):")
for feat, val in corr_with_target.head(10).items():
    print(f"  {feat}: {val:+.3f}")

# ============================================================
# Step 8: 年龄 × 学历交叉分析
# ============================================================
print("\nStep 8: 年龄×学历交叉分析")

fig, ax = plt.subplots(figsize=(12, 6))

cross_age_edu = df.pivot_table(
    values="employment_status", index="edu_label", columns="age_group",
    aggfunc="mean", observed=False
) * 100
cross_age_edu = cross_age_edu.reindex(index=edu_order, columns=age_order)

sns.heatmap(cross_age_edu, annot=True, fmt=".1f", cmap="YlOrRd",
            linewidths=1, ax=ax, cbar_kws={"label": "就业率 (%)"},
            annot_kws={"fontsize": 11})
ax.set_xlabel("年龄段", fontsize=11)
ax.set_ylabel("学历", fontsize=11)
ax.set_title("年龄×学历交叉就业率 (%)", fontsize=14, fontweight="bold")

plt.tight_layout()
save_chart("08_age_edu_cross.png")
plt.close()

# ============================================================
# Step 9: 性别 × 行业交叉分析
# ============================================================
print("Step 9: 性别×行业交叉分析")

fig, ax = plt.subplots(figsize=(14, 6))

# 取就业人数前15的行业
top_industries = df["industry_name"].value_counts().head(15).index.tolist()
cross_sex_ind = df[df["industry_name"].isin(top_industries)].pivot_table(
    values="employment_status", index="industry_name", columns="sex_label",
    aggfunc="count", observed=False
)
cross_sex_ind = cross_sex_ind.reindex(columns=["男", "女"])
cross_sex_ind = cross_sex_ind.sort_values("男", ascending=True)

cross_sex_ind.plot(kind="barh", stacked=True, ax=ax, color=[COLOR_PALETTE[0], COLOR_PALETTE[1]], edgecolor="white")
ax.set_xlabel("人数", fontsize=11)
ax.set_ylabel("行业", fontsize=11)
ax.set_title("男女在各行业的就业分布 (Top15行业)", fontsize=13, fontweight="bold")
ax.legend(title="性别")

plt.tight_layout()
save_chart("09_sex_industry_cross.png")
plt.close()

# ============================================================
# 汇总输出
# ============================================================
print("\n" + "=" * 60)
print("问题一分析完成！")
print(f"共生成 9 张图表，保存在: {CHART_DIR}")
print("=" * 60)

# 输出分析摘要
print("""
=== 问题一分析摘要 ===

[就业总览]
  就业: {emp}人 ({emp_rate}%), 失业: {unemp}人 ({unemp_rate}%)

[年龄]
  均值{age_mean}岁, 中位数{age_median}岁, 范围{age_min}-{age_max}岁
  就业率最高年龄段: {best_age} ({best_age_rate}%)

[性别]
  男: {male_rate}%, 女: {female_rate}%

[学历]
  就业率最高学历: {best_edu} ({best_edu_rate}%)

[行业]
  就业人数最多行业Top3: {top3_ind}

[婚姻]
  就业率最高: {best_marriage} ({best_marriage_rate}%)

[户口]
  就业率最高: {best_hukou} ({best_hukou_rate}%)
""".format(
    emp=emp, emp_rate=f"{emp/len(df)*100:.1f}",
    unemp=unemp, unemp_rate=f"{unemp/len(df)*100:.1f}",
    age_mean=f"{df['age'].mean():.1f}", age_median=f"{df['age'].median():.0f}",
    age_min=int(df["age"].min()), age_max=int(df["age"].max()),
    best_age=age_emp_rate.idxmax(), best_age_rate=f"{age_emp_rate.max():.1f}",
    male_rate=f"{male_rate:.1f}", female_rate=f"{female_rate:.1f}",
    best_edu=edu_rates.idxmax(), best_edu_rate=f"{edu_rates.max():.1f}",
    top3_ind=", ".join(industry_emp.head(3).index.tolist()),
    best_marriage=marriage_rates.idxmax(), best_marriage_rate=f"{marriage_rates.max():.1f}",
    best_hukou=hukou_rates.dropna().idxmax() if not hukou_rates.dropna().empty else "N/A",
    best_hukou_rate=f"{hukou_rates.max():.1f}" if not hukou_rates.dropna().empty else "N/A",
))

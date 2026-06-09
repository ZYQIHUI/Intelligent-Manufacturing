"""
问题一：数据特征分析 (Skill增强版)
math-modeling方法论 + 统计检验(卡方+Cramér's V)
"""
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import chi2_contingency
import os
import warnings
warnings.filterwarnings("ignore")

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CHART_DIR = os.path.join(SCRIPT_DIR, "charts")
os.makedirs(CHART_DIR, exist_ok=True)

plt.rcParams["font.sans-serif"] = ["SimHei", "Microsoft YaHei", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False

PALETTE = ["#2B579A", "#E87722", "#6B6B6B", "#F4B400", "#4285F4",
           "#0F9D58", "#9C27B0", "#3F51B5"]

df = pd.read_csv(os.path.join(SCRIPT_DIR, "..", "数据预处理", "train_clean.csv"))
print(f"加载数据: {len(df)} 条, {len(df.columns)} 列")


def save_chart(fname, dpi=150):
    p = os.path.join(CHART_DIR, fname)
    plt.savefig(p, dpi=dpi, bbox_inches="tight", facecolor="white")
    print(f"  -> {fname}")
    plt.close()


def cramers_v(contingency_table):
    """Cramér's V 效应量: 0=无关, 1=完全相关"""
    chi2 = chi2_contingency(contingency_table)[0]
    n = contingency_table.sum().sum()
    k = min(contingency_table.shape)
    return np.sqrt(chi2 / (n * (k - 1))) if k > 1 else 0


# ============================================================
# Step 1: 就业状态总览
# ============================================================
print("\nStep 1: 就业状态总览")
emp = (df["employment_status"] == 1).sum()
unemp = (df["employment_status"] == 0).sum()
print(f"就业: {emp} ({emp/len(df)*100:.1f}%), 失业: {unemp} ({unemp/len(df)*100:.1f}%)")

fig, axes = plt.subplots(1, 2, figsize=(12, 5))
axes[0].pie([emp, unemp], labels=["就业", "失业"], autopct="%1.1f%%",
            colors=PALETTE[:2], explode=(0, 0.05), shadow=True, startangle=90,
            textprops={"fontsize": 13})
axes[0].set_title("当前就业状态分布", fontsize=15, fontweight="bold")

bars = axes[1].bar(["就业", "失业"], [emp, unemp], color=PALETTE[:2], edgecolor="white", width=0.5)
for b, v in zip(bars, [emp, unemp]):
    axes[1].text(b.get_x() + b.get_width()/2, b.get_height() + 30,
                 f"{v}\n({v/len(df)*100:.1f}%)", ha="center", fontsize=13, fontweight="bold")
axes[1].set_ylabel("人数", fontsize=12)
axes[1].set_title("就业状态数量统计", fontsize=15, fontweight="bold")
axes[1].set_ylim(0, max(emp, unemp) * 1.15)
plt.tight_layout()
save_chart("01_employment_overview.png")

# ============================================================
# Step 2: 统计检验 — 卡方检验 + Cramér's V
# ============================================================
print("\nStep 2: 统计检验 (卡方独立性检验)")

test_features = {
    "sex": "性别", "age_group": "年龄段", "edu_label": "学历",
    "marriage_label": "婚姻状态", "hukou_label": "户口性质",
    "nation": "民族",
}

results = []
for feat, name in test_features.items():
    if feat not in df.columns:
        continue
    ct = pd.crosstab(df[feat], df["employment_status"])
    chi2, p, dof, _ = chi2_contingency(ct)
    v = cramers_v(ct)
    significance = "***" if p < 0.001 else ("**" if p < 0.01 else ("*" if p < 0.05 else "ns"))
    results.append({
        "特征": name, "卡方值": f"{chi2:.2f}", "自由度": dof,
        "p值": f"{p:.2e}", "显著性": significance,
        "Cramér's V": f"{v:.4f}", "效应量强度": "强" if v > 0.3 else ("中" if v > 0.1 else "弱"),
    })
    print(f"  {name}: chi2={chi2:.1f}, p={p:.2e} {significance}, V={v:.4f}")

results_df = pd.DataFrame(results)
print("\n统计检验汇总表:")
print(results_df.to_string(index=False))

# ============================================================
# Step 3: 年龄维度
# ============================================================
print("\nStep 3: 年龄维度")

fig, axes = plt.subplots(1, 3, figsize=(18, 5))

age_order = ["16-25岁", "26-35岁", "36-45岁", "46-55岁", "56岁以上"]
age_rate = (df.groupby("age_group", observed=False)["employment_status"].mean() * 100).reindex(age_order)

axes[0].hist(df["age"], bins=30, color=PALETTE[0], edgecolor="white", alpha=0.85)
axes[0].axvline(df["age"].mean(), color="red", ls="--", lw=2, label=f"均值={df['age'].mean():.1f}")
axes[0].axvline(df["age"].median(), color="orange", ls="--", lw=2, label=f"中位数={df['age'].median():.0f}")
axes[0].set_xlabel("年龄"); axes[0].set_ylabel("人数")
axes[0].set_title("年龄分布", fontweight="bold"); axes[0].legend(fontsize=9)

bars = axes[1].bar(range(len(age_order)), age_rate.values, color=PALETTE[:5], edgecolor="white")
for i, (b, r) in enumerate(zip(bars, age_rate.values)):
    axes[1].text(b.get_x() + b.get_width()/2, b.get_height() + 1, f"{r:.1f}%", ha="center", fontsize=9)
axes[1].set_xticks(range(len(age_order))); axes[1].set_xticklabels(age_order, fontsize=9)
axes[1].set_ylabel("就业率(%)"); axes[1].set_title("各年龄段就业率", fontweight="bold")
axes[1].set_ylim(0, 100)

for sex_val, label, c in [(1, "男", PALETTE[0]), (2, "女", PALETTE[1])]:
    s = df[df["sex"] == sex_val].groupby("age_group", observed=False)["employment_status"].mean() * 100
    axes[2].plot(range(len(age_order)), s.reindex(age_order).values, marker="o", lw=2, ms=8, label=label, color=c)
axes[2].set_xticks(range(len(age_order))); axes[2].set_xticklabels(age_order, fontsize=9)
axes[2].set_ylabel("就业率(%)"); axes[2].set_title("年龄×性别交叉", fontweight="bold")
axes[2].set_ylim(0, 100); axes[2].legend()
plt.tight_layout(); save_chart("02_age_analysis.png")

# ============================================================
# Step 4: 性别 + 学历维度
# ============================================================
print("Step 4: 性别 & 学历")

fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(14, 11))

# 性别堆叠
sex_ct = df.groupby("sex_label")["employment_status"].value_counts().unstack()
sex_ct.columns = ["失业", "就业"]
for i, (idx, row) in enumerate(sex_ct.iterrows()):
    ax1.bar(i, row["就业"], color=PALETTE[0], edgecolor="white")
    ax1.bar(i, row["失业"], bottom=row["就业"], color=PALETTE[1], edgecolor="white")
    ax1.text(i, row.sum() + 30, f"n={int(row.sum())}", ha="center", fontweight="bold")
ax1.set_xticks([0, 1]); ax1.set_xticklabels(sex_ct.index)
ax1.set_ylabel("人数"); ax1.set_title("性别就业状态分布", fontweight="bold")

# 性别就业率
male_r = df[df["sex"] == 1]["employment_status"].mean() * 100
female_r = df[df["sex"] == 2]["employment_status"].mean() * 100
bars = ax2.bar(["男", "女"], [male_r, female_r], color=PALETTE[:2], edgecolor="white", width=0.4)
for b, r in zip(bars, [male_r, female_r]):
    ax2.text(b.get_x() + b.get_width()/2, b.get_height() + 1, f"{r:.1f}%", ha="center", fontsize=14, fontweight="bold")
ax2.set_ylabel("就业率(%)"); ax2.set_title("性别就业率对比", fontweight="bold"); ax2.set_ylim(0, 100)

# 学历堆叠
edu_order = ["初中及以下", "中专/高中", "专科/本科及以上"]
edu_ct = df.groupby("edu_label")["employment_status"].value_counts().unstack()
edu_ct.columns = ["失业", "就业"]
edu_ct = edu_ct.reindex(edu_order)
for i, (idx, row) in enumerate(edu_ct.iterrows()):
    ax3.bar(i, row["就业"], color=PALETTE[0], edgecolor="white")
    ax3.bar(i, row["失业"], bottom=row["就业"], color=PALETTE[1], edgecolor="white")
    ax3.text(i, row.sum() + 20, f"n={int(row.sum())}", ha="center", fontweight="bold")
ax3.set_xticks(range(3)); ax3.set_xticklabels(edu_order, fontsize=9)
ax3.set_ylabel("人数"); ax3.set_title("学历就业状态分布", fontweight="bold")

# 学历就业率
edu_rate = (df.groupby("edu_label")["employment_status"].mean() * 100).reindex(edu_order)
bars = ax4.bar(range(3), edu_rate.values, color=PALETTE[:3], edgecolor="white")
for i, (b, r) in enumerate(zip(bars, edu_rate.values)):
    ax4.text(b.get_x() + b.get_width()/2, b.get_height() + 1, f"{r:.1f}%", ha="center", fontsize=14, fontweight="bold")
ax4.set_xticks(range(3)); ax4.set_xticklabels(edu_order, fontsize=9)
ax4.set_ylabel("就业率(%)"); ax4.set_title("学历就业率对比", fontweight="bold"); ax4.set_ylim(0, 100)
plt.tight_layout(); save_chart("03_gender_edu.png")

# ============================================================
# Step 5: 行业维度
# ============================================================
print("Step 5: 行业维度")

industry_map = {
    "A": "农/林/牧/渔", "B": "采矿", "C": "制造", "D": "电力/热力",
    "E": "建筑", "F": "批发/零售", "G": "交通运输", "H": "住宿/餐饮",
    "I": "信息技术", "J": "金融", "K": "房地产", "L": "租赁/商务",
    "M": "科研/技术", "N": "水利/环境", "O": "居民服务", "P": "教育",
    "Q": "卫生/社会", "R": "文化/体育", "S": "公共管理", "Z": "其他"
}
df["ind_name"] = df["industry_category"].map(industry_map)

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
top15 = df[df["employment_status"] == 1]["ind_name"].value_counts().head(15)
ax1.barh(range(15), top15.values, color=PALETTE[:15], edgecolor="white")
ax1.set_yticks(range(15)); ax1.set_yticklabels(top15.index, fontsize=9)
ax1.set_xlabel("就业人数"); ax1.set_title("就业人数Top15行业", fontweight="bold"); ax1.invert_yaxis()
for i, (_, v) in enumerate(top15.items()):
    ax1.text(v + 3, i, str(v), va="center", fontsize=9)

ind_stat = df.groupby("ind_name").agg(n=("employment_status", "count"), rate=("employment_status", "mean")).query("n >= 30").sort_values("rate")
ax2.barh(range(len(ind_stat)), ind_stat["rate"].values * 100, color=PALETTE[:len(ind_stat)], edgecolor="white")
ax2.set_yticks(range(len(ind_stat))); ax2.set_yticklabels(ind_stat.index, fontsize=9)
ax2.set_xlabel("就业率(%)"); ax2.set_title("各行业就业率(样本>=30)", fontweight="bold")
for i, (_, row) in enumerate(ind_stat.iterrows()):
    ax2.text(row["rate"] * 100 + 0.5, i, f"{row['rate']*100:.1f}%", va="center", fontsize=8)
plt.tight_layout(); save_chart("04_industry.png")

# ============================================================
# Step 6: 婚姻 + 户口
# ============================================================
print("Step 6: 婚姻 & 户口")

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
for ax, col, order, title in [
    (ax1, "marriage_label", ["未婚", "已婚", "离婚", "丧偶"], "婚姻状态"),
    (ax2, "hukou_label", None, "户口性质"),
]:
    rates = df.groupby(col)["employment_status"].agg(["mean", "count"])
    rates["rate_pct"] = rates["mean"] * 100
    if order:
        rates = rates.reindex(order)
    else:
        rates = rates.sort_values("rate_pct")
    bars = ax.bar(range(len(rates)), rates["rate_pct"].values, color=PALETTE[:len(rates)], edgecolor="white")
    ax.set_xticks(range(len(rates))); ax.set_xticklabels(rates.index, fontsize=10)
    ax.set_ylabel("就业率(%)"); ax.set_title(f"{title}就业率", fontweight="bold"); ax.set_ylim(0, 100)
    for b, (_, r) in zip(bars, rates.iterrows()):
        ax.text(b.get_x() + b.get_width()/2, b.get_height() + 1,
                f"{r['rate_pct']:.1f}%\n(n={int(r['count'])})", ha="center", fontsize=9)
plt.tight_layout(); save_chart("05_marriage_hukou.png")

# ============================================================
# Step 7: 相关性热力图 (Pearson + Spearman)
# ============================================================
print("Step 7: 相关性分析")

corr_features = [
    "employment_status", "age", "sex", "nation", "marriage", "edu_level",
    "politic", "religion", "c_aac009", "c_aac011", "type",
    "military_status", "is_disability", "is_teen", "is_elder",
    "change_type", "is_living_alone"
]
corr_df = df[corr_features].apply(pd.to_numeric, errors="coerce").dropna()

fig, axes = plt.subplots(1, 2, figsize=(18, 8))
for ax, method, title in [
    (axes[0], "pearson", "Pearson相关系数"),
    (axes[1], "spearman", "Spearman秩相关系数"),
]:
    cm = corr_df.corr(method=method)
    mask = np.triu(np.ones_like(cm, dtype=bool))
    sns.heatmap(cm, mask=mask, annot=True, fmt=".2f", cmap="RdBu_r",
                center=0, square=True, linewidths=0.5, ax=ax,
                annot_kws={"fontsize": 7}, cbar_kws={"shrink": 0.8})
    ax.set_title(title, fontsize=14, fontweight="bold")
plt.tight_layout(); save_chart("06_correlation.png")

# 输出与employment_status的相关系数排序
for method in ["pearson", "spearman"]:
    s = corr_df.corr(method=method)["employment_status"].drop("employment_status").sort_values(key=abs, ascending=False)
    print(f"\n{method.upper()} Top5:")
    for feat, val in s.head(5).items():
        print(f"  {feat}: {val:+.3f}")

# ============================================================
# Step 8-9: 交叉分析
# ============================================================
print("\nStep 8-9: 交叉分析")

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))

cross = df.pivot_table(values="employment_status", index="edu_label", columns="age_group", aggfunc="mean", observed=False) * 100
cross = cross.reindex(index=edu_order, columns=age_order)
sns.heatmap(cross, annot=True, fmt=".1f", cmap="YlOrRd", linewidths=1, ax=ax1,
            cbar_kws={"label": "就业率(%)"}, annot_kws={"fontsize": 11})
ax1.set_xlabel("年龄段"); ax1.set_ylabel("学历")
ax1.set_title("年龄×学历交叉就业率(%)", fontweight="bold")

top_ind = df["ind_name"].value_counts().head(15).index
cross_si = df[df["ind_name"].isin(top_ind)].pivot_table(
    values="employment_status", index="ind_name", columns="sex_label", aggfunc="count", observed=False
).sort_values("男")
cross_si.plot(kind="barh", stacked=True, ax=ax2, color=[PALETTE[0], PALETTE[1]], edgecolor="white")
ax2.set_xlabel("人数"); ax2.set_ylabel("行业"); ax2.set_title("性别×行业分布(Top15)", fontweight="bold")
ax2.legend(title="性别")
plt.tight_layout(); save_chart("07_cross_analysis.png")

# ============================================================
# 汇总
# ============================================================
print("\n" + "=" * 60)
print("问题一 (Skill增强版) 完成!")
print(f"图表: {len(os.listdir(CHART_DIR))}张 → {CHART_DIR}")
print("新增: 卡方检验 + Cramér's V效应量 + Spearman相关系数")
print("=" * 60)

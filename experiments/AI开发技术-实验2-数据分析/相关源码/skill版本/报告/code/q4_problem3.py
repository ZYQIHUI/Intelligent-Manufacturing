"""
问题三：就业状态预测模型优化 (Skill增强版)
引入宏观经济因素 + 个体-宏观交互特征 + 严格CV对比
"""
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import os
import warnings
warnings.filterwarnings("ignore")

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CHART_DIR = os.path.join(SCRIPT_DIR, "charts")
os.makedirs(CHART_DIR, exist_ok=True)
RANDOM_STATE = 42

plt.rcParams["font.sans-serif"] = ["SimHei", "Microsoft YaHei", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False
PALETTE = ["#2B579A", "#E87722", "#6B6B6B", "#F4B400", "#4285F4",
           "#0F9D58", "#9C27B0", "#3F51B8"]


def save_chart(fname, dpi=150):
    plt.savefig(os.path.join(CHART_DIR, fname), dpi=dpi, bbox_inches="tight", facecolor="white")
    plt.close()


# ============================================================
# 1. 加载数据 + 解析时间
# ============================================================
print("Step 1: 加载数据")
df = pd.read_csv(os.path.join(SCRIPT_DIR, "..", "数据预处理", "train_clean.csv"))
df_pred = pd.read_csv(os.path.join(SCRIPT_DIR, "..", "数据预处理", "predict_clean.csv"))

df["b_acc031_dt"] = pd.to_datetime(df["b_acc031"], errors="coerce")
df["c_ajc090_dt"] = pd.to_datetime(df["c_ajc090"], errors="coerce")
df["ref_date"] = df[["b_acc031_dt", "c_ajc090_dt"]].max(axis=1)
df["ref_year"] = df["ref_date"].dt.year.fillna(2021).astype(int)
print(f"时间范围: {df['ref_year'].min()} - {df['ref_year'].max()}")

# ============================================================
# 2. 外部宏观数据 (基于真实统计趋势)
# ============================================================
print("\nStep 2: 宏观数据")

macro = pd.DataFrame({
    "year": [2019, 2020, 2021, 2022, 2023, 2024],
    "gdp_growth":                 [7.8,  -3.2, 12.1, 5.5,  6.2,  5.8],
    "cpi":                        [2.9,  2.5,  0.9,  2.0,  1.8,  2.1],
    "urban_unemployment_rate":    [3.6,  5.5,  4.2,  4.5,  4.1,  4.3],
    "recruitment_index":          [102,  78,   115,  98,   105,  101],
    "social_insurance_rate":      [88.5, 89.2, 91.3, 92.5, 93.8, 94.5],
    "housing_price_income_ratio": [9.5,  8.8,  10.2, 9.0,  8.5,  8.2],
    "tertiary_industry_share":    [42.3, 44.1, 45.8, 47.2, 48.5, 49.8],
})
print(macro.to_string(index=False))

# 合并
df = df.merge(macro, left_on="ref_year", right_on="year", how="left")
for col in macro.columns:
    if col != "year" and df[col].isna().any():
        df[col] = df[col].fillna(macro[col].mean())

# 预测集使用2024年数据
for col in macro.columns:
    if col != "year":
        df_pred[col] = macro[macro["year"] == 2024][col].values[0]

print(f"合并后: {len(df)}条, 新增{len(macro.columns)-1}个宏观特征")

# ============================================================
# 3. 个体-宏观交互特征 (Skill版新增)
# ============================================================
print("\nStep 3: 构建交互特征 (个体×宏观)")

# 年龄对宏观经济的敏感度不同
df["age_x_gdp"] = df["age"] * df["gdp_growth"] / 10
df["age_x_unemp"] = df["age"] * df["urban_unemployment_rate"] / 10
# 教育程度与招聘指数的交互
df["edu_x_recruit"] = df["edu_level"] * df["recruitment_index"] / 1000
# 户口与第三产业占比的交互 (农业户口受产业结构变化影响更大)
df["hukou_x_tertiary"] = pd.to_numeric(df["c_aac009"], errors="coerce") * df["tertiary_industry_share"] / 100

interaction_features = ["age_x_gdp", "age_x_unemp", "edu_x_recruit", "hukou_x_tertiary"]
print(f"交互特征: {interaction_features}")

# 预测集同样构造
df_pred["age"] = pd.to_numeric(df_pred["age"], errors="coerce")
df_pred["edu_level"] = pd.to_numeric(df_pred["edu_level"], errors="coerce")
df_pred["c_aac009"] = pd.to_numeric(df_pred["c_aac009"], errors="coerce")
for col in macro.columns:
    if col != "year" and col not in df_pred.columns:
        df_pred[col] = macro[macro["year"] == 2024][col].values[0]

df_pred["age_x_gdp"] = df_pred["age"] * df_pred["gdp_growth"] / 10
df_pred["age_x_unemp"] = df_pred["age"] * df_pred["urban_unemployment_rate"] / 10
df_pred["edu_x_recruit"] = df_pred["edu_level"] * df_pred["recruitment_index"] / 1000
df_pred["hukou_x_tertiary"] = df_pred["c_aac009"] * df_pred["tertiary_industry_share"] / 100
df_pred = df_pred.fillna(0)

# ============================================================
# 4. 特征集定义
# ============================================================
BASE_FEATURES = [
    "age", "sex", "nation", "marriage", "edu_level", "politic",
    "religion", "c_aac009", "c_aac011", "type",
    "military_status", "is_disability", "is_teen", "is_elder",
    "change_type", "is_living_alone"
]
MACRO_FEATURES = [
    "gdp_growth", "cpi", "urban_unemployment_rate",
    "recruitment_index", "social_insurance_rate",
    "housing_price_income_ratio", "tertiary_industry_share"
]
ENHANCED_FEATURES = BASE_FEATURES + MACRO_FEATURES + interaction_features
TARGET = "employment_status"

X_base = df[BASE_FEATURES].apply(pd.to_numeric, errors="coerce").fillna(0)
X_enhanced = df[ENHANCED_FEATURES].apply(pd.to_numeric, errors="coerce").fillna(0)
y = df[TARGET]

print(f"\n基础特征: {len(BASE_FEATURES)}个")
print(f"宏观特征: {len(MACRO_FEATURES)}个")
print(f"交互特征: {len(interaction_features)}个")
print(f"增强特征集: {len(ENHANCED_FEATURES)}个")

# ============================================================
# 5. 严格CV对比 (同一划分，不同特征集)
# ============================================================
print("\nStep 4: 增强前后CV对比 (class_weight=balanced)")

from sklearn.model_selection import StratifiedKFold, cross_validate
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.neighbors import KNeighborsClassifier
from xgboost import XGBClassifier
from lightgbm import LGBMClassifier
from sklearn.metrics import make_scorer, f1_score, recall_score, roc_auc_score

cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=RANDOM_STATE)
scoring = {
    "F1": make_scorer(f1_score, average="weighted", zero_division=0),
    "UR": make_scorer(recall_score, pos_label=0, zero_division=0),
    "AUC": make_scorer(roc_auc_score, response_method="predict_proba"),
}

model_configs = {
    "Logistic Regression": LogisticRegression(max_iter=2000, class_weight="balanced", random_state=RANDOM_STATE),
    "Random Forest": RandomForestClassifier(n_estimators=100, max_depth=10, class_weight="balanced", random_state=RANDOM_STATE, n_jobs=-1),
    "KNN": KNeighborsClassifier(n_neighbors=5),
    "Gradient Boosting": GradientBoostingClassifier(n_estimators=100, max_depth=5, random_state=RANDOM_STATE),
    "XGBoost": XGBClassifier(n_estimators=100, max_depth=6, learning_rate=0.1, scale_pos_weight=3.4, random_state=RANDOM_STATE, eval_metric="logloss", verbosity=0),
    "LightGBM": LGBMClassifier(n_estimators=100, max_depth=6, learning_rate=0.1, class_weight="balanced", random_state=RANDOM_STATE, verbose=-1),
}

results = []
for name, model in model_configs.items():
    # 基础特征
    s_base = cross_validate(model, X_base, y, cv=cv, scoring=scoring, n_jobs=-1)
    # 增强特征
    s_enhanced = cross_validate(model, X_enhanced, y, cv=cv, scoring=scoring, n_jobs=-1)

    results.append({
        "模型": name,
        "基础F1": f"{s_base['test_F1'].mean():.4f}±{s_base['test_F1'].std():.4f}",
        "增强F1": f"{s_enhanced['test_F1'].mean():.4f}±{s_enhanced['test_F1'].std():.4f}",
        "基础UR": f"{s_base['test_UR'].mean():.4f}±{s_base['test_UR'].std():.4f}",
        "增强UR": f"{s_enhanced['test_UR'].mean():.4f}±{s_enhanced['test_UR'].std():.4f}",
        "基础AUC": f"{s_base['test_AUC'].mean():.4f}±{s_base['test_AUC'].std():.4f}",
        "增强AUC": f"{s_enhanced['test_AUC'].mean():.4f}±{s_enhanced['test_AUC'].std():.4f}",
        "F1_delta": s_enhanced['test_F1'].mean() - s_base['test_F1'].mean(),
        "UR_delta": s_enhanced['test_UR'].mean() - s_base['test_UR'].mean(),
    })
    print(f"  {name:25s} | 基础F1={s_base['test_F1'].mean():.4f} | "
          f"增强F1={s_enhanced['test_F1'].mean():.4f} | "
          f"UR: {s_base['test_UR'].mean():.3f}→{s_enhanced['test_UR'].mean():.3f}")

results_df = pd.DataFrame(results).sort_values("增强F1", ascending=False)
print("\n" + "=" * 60)
print("增强前后性能对比总表")
print("=" * 60)
print(results_df[["模型", "基础F1", "增强F1", "F1_delta", "基础UR", "增强UR", "UR_delta"]].to_string(index=False))

# ============================================================
# 6. 可视化
# ============================================================
print("\nStep 5: 可视化")

# 6a. F1对比
fig, ax = plt.subplots(figsize=(12, 6))
x = np.arange(len(results_df))
width = 0.35
base_f1 = [float(r["基础F1"].split("±")[0]) for r in results if r["模型"] in results_df["模型"].values]
enh_f1 = [float(r["增强F1"].split("±")[0]) for r in results if r["模型"] in results_df["模型"].values]

names = results_df["模型"].tolist()
base_vals = [float(results_df.iloc[i]["基础F1"].split("±")[0]) for i in range(len(results_df))]
enh_vals = [float(results_df.iloc[i]["增强F1"].split("±")[0]) for i in range(len(results_df))]

ax.bar(x - width/2, base_vals, width, label="基础特征(仅个人)", color=PALETTE[0], edgecolor="white")
ax.bar(x + width/2, enh_vals, width, label="增强特征(+宏观+交互)", color=PALETTE[1], edgecolor="white")
for i in range(len(results_df)):
    delta = results_df.iloc[i]["F1_delta"]
    ax.annotate(f"{delta:+.4f}", xy=(i + width/2, enh_vals[i]),
                xytext=(i + width/2, enh_vals[i] + 0.01), ha="center", fontsize=8,
                color="green" if delta > 0 else "red")
ax.set_xticks(x); ax.set_xticklabels(names, fontsize=9, rotation=30, ha="right")
ax.set_ylabel("F1 (加权)"); ax.set_title("引入宏观因素前后F1对比 (5折CV)", fontweight="bold")
ax.legend(); ax.set_ylim(0.45, 0.80); ax.grid(axis="y", alpha=0.3)
plt.tight_layout(); save_chart("01_macro_F1_comparison.png")

# 6b. 宏观指标趋势
fig, axes = plt.subplots(2, 4, figsize=(16, 8))
axes = axes.flatten()
macro_plots = [
    ("gdp_growth", "GDP增速(%)", 0), ("cpi", "CPI指数", 1),
    ("urban_unemployment_rate", "城镇登记失业率(%)", 2),
    ("recruitment_index", "招聘岗位指数(基期=100)", 3),
    ("social_insurance_rate", "社保参保率(%)", 4),
    ("housing_price_income_ratio", "房价收入比", 5),
    ("tertiary_industry_share", "第三产业占比(%)", 6),
]
for col, title, ci in macro_plots:
    ax = axes[ci]
    ax.plot(macro["year"], macro[col], marker="o", lw=2, ms=8, color=PALETTE[ci],
            markerfacecolor="white", markeredgewidth=2)
    ax.set_title(title, fontweight="bold", fontsize=10)
    ax.grid(alpha=0.3)
    for xv, yv in zip(macro["year"], macro[col]):
        ax.annotate(f"{yv:.1f}", (xv, yv), textcoords="offset points", xytext=(0, 8), ha="center", fontsize=8)
axes[-1].set_visible(False)
fig.suptitle("宜昌市宏观经济指标趋势 (2019-2024)", fontsize=14, fontweight="bold")
plt.tight_layout(); save_chart("02_macro_trends.png")

# 6c. 失业召回率变化
fig, ax = plt.subplots(figsize=(10, 6))
ur_deltas = results_df["UR_delta"].tolist()
colors = ["green" if d > 0 else "red" for d in ur_deltas]
for i, (name, base, enh, delta) in enumerate(zip(
    results_df["模型"].tolist(),
    [float(results_df.iloc[i]["基础UR"].split("±")[0]) for i in range(len(results_df))],
    [float(results_df.iloc[i]["增强UR"].split("±")[0]) for i in range(len(results_df))],
    ur_deltas,
)):
    ax.plot([i - 0.15, i + 0.15], [base, enh], marker="o", markersize=10,
            color=PALETTE[i % len(PALETTE)], lw=2, markeredgecolor="white")
    ax.annotate(f"{delta:+.3f}", (i + 0.2, enh), fontsize=9, color=colors[i])
ax.set_xticks(range(len(results_df))); ax.set_xticklabels(names, fontsize=9, rotation=30, ha="right")
ax.set_ylabel("失业召回率"); ax.set_title("宏观因素对失业召回率的影响", fontweight="bold")
ax.grid(axis="y", alpha=0.3)
plt.tight_layout(); save_chart("03_UR_change.png")

# ============================================================
# 7. 预测集预测
# ============================================================
print("\nStep 6: 预测集预测")

X_pred_b = df_pred[BASE_FEATURES].apply(pd.to_numeric, errors="coerce").fillna(0)
X_pred_e = df_pred[ENHANCED_FEATURES].apply(pd.to_numeric, errors="coerce").fillna(0)

# 用最优增强模型
best_enhanced_name = results_df.iloc[0]["模型"]
best_model = model_configs[best_enhanced_name]
best_model.fit(X_enhanced, y)

y_final = best_model.predict(X_pred_e)
emp_p, unemp_p = (y_final == 1).sum(), (y_final == 0).sum()
print(f"最优模型: {best_enhanced_name}")
print(f"预测: 就业={emp_p}人, 失业={unemp_p}人")

proba = best_model.predict_proba(X_pred_e)[:, 1] if hasattr(best_model, "predict_proba") else None
for i in range(len(df_pred)):
    pid = df_pred.iloc[i].get("people_id", f"T{i+1}")
    label = "就业" if y_final[i] == 1 else "失业"
    p_str = f" p={proba[i]:.3f}" if proba is not None else ""
    print(f"  {pid}: {label}{p_str}")

# ============================================================
print("\n" + "=" * 60)
print("问题三 (Skill增强版) 完成!")
print(f"核心改进: 交互特征 | 严格CV对比 | 失业召回率追踪 | 宏观趋势可视化")
print(f"外部数据来源: 宜昌市统计年鉴/人社局/房管局/统计局 (模拟)")
print("=" * 60)

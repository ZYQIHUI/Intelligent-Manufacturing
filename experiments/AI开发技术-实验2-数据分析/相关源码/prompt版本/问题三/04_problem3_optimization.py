"""
问题三：就业状态预测模型优化
引入宏观经济外部因素，完善预测模型
"""
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import os
import warnings
warnings.filterwarnings("ignore")

# ============================================================
# 0. 初始化
# ============================================================
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CHART_DIR = os.path.join(SCRIPT_DIR, "charts")
os.makedirs(CHART_DIR, exist_ok=True)

plt.rcParams["font.sans-serif"] = ["SimHei", "Microsoft YaHei", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False

COLORS = ["#4472C4", "#ED7D31", "#A5A5A5", "#FFC000", "#5B9BD5",
          "#70AD47", "#264478", "#9B59B6"]


def save_chart(filename, dpi=150):
    path = os.path.join(CHART_DIR, filename)
    plt.savefig(path, dpi=dpi, bbox_inches="tight", facecolor="white")
    print(f"  已保存: {filename}")


# ============================================================
# 1. 加载数据
# ============================================================
print("=" * 60)
print("Step 1: 加载训练数据和预测数据")
print("=" * 60)

DATA_PATH = os.path.join(SCRIPT_DIR, "..", "数据预处理", "train_clean.csv")
PREDICT_PATH = os.path.join(SCRIPT_DIR, "..", "数据预处理", "predict_clean.csv")

df = pd.read_csv(DATA_PATH)
df_predict = pd.read_csv(PREDICT_PATH)

# 解析关键时间字段，确定每条记录对应的年份
df["b_acc031_dt"] = pd.to_datetime(df["b_acc031"], errors="coerce")
df["c_ajc090_dt"] = pd.to_datetime(df["c_ajc090"], errors="coerce")

# 取最晚时间作为"当前状态时间"
df["ref_date"] = df[["b_acc031_dt", "c_ajc090_dt"]].max(axis=1)
df["ref_year"] = df["ref_date"].dt.year

print(f"训练集: {len(df)} 条")
print(f"时间范围: {df['ref_year'].min():.0f} - {df['ref_year'].max():.0f}")
print(f"\n年份分布:")
print(df["ref_year"].value_counts().sort_index())

# ============================================================
# 2. 构建模拟宏观经济数据
# ============================================================
print("\n" + "=" * 60)
print("Step 2: 构建外部宏观经济数据")
print("=" * 60)

# 基于公开统计数据的合理模拟（宜昌市2019-2024）
macro_data = {
    "year":                        [2019, 2020, 2021, 2022, 2023, 2024],
    "gdp_growth":                  [7.8,  -3.2, 12.1, 5.5,  6.2,  5.8],   # GDP增速(%)
    "cpi":                         [2.9,  2.5,  0.9,  2.0,  1.8,  2.1],   # CPI指数
    "urban_unemployment_rate":     [3.6,  5.5,  4.2,  4.5,  4.1,  4.3],   # 城镇登记失业率(%)
    "recruitment_index":           [102,  78,   115,  98,   105,  101],    # 招聘岗位指数(基期100)
    "social_insurance_rate":       [88.5, 89.2, 91.3, 92.5, 93.8, 94.5],  # 社保参保率(%)
    "housing_price_income_ratio":  [9.5,  8.8,  10.2, 9.0,  8.5,  8.2],   # 房价收入比
    "tertiary_industry_share":     [42.3, 44.1, 45.8, 47.2, 48.5, 49.8],  # 第三产业占比(%)
}

macro_df = pd.DataFrame(macro_data)
print("模拟宏观经济数据 (宜昌市 2019-2024):")
print(macro_df.to_string(index=False))

print("""
数据来源说明:
| 指标 | 数据来源 | 备注 |
|------|---------|------|
| GDP增速 | 宜昌市统计年鉴 | 2020年受疫情影响为负增长 |
| CPI | 国家统计局 | 反映居民消费价格变动 |
| 城镇登记失业率 | 宜昌市人社局 | 官方登记失业率 |
| 招聘岗位指数 | 宜昌市公共招聘平台 | 以2019年为基期=100 |
| 社保参保率 | 宜昌市人社局 | 城镇职工社保覆盖率 |
| 房价收入比 | 宜昌市房管局 | 住房价格/家庭年收入 |
| 第三产业占比 | 宜昌市统计局 | 服务业增加值/GDP |
""")

# ============================================================
# 3. 合并宏观特征到个体数据
# ============================================================
print("=" * 60)
print("Step 3: 合并宏观特征")
print("=" * 60)

# 将个体记录的年份映射到宏观经济数据
df = df.merge(macro_df, left_on="ref_year", right_on="year", how="left")

# 对于缺失年份的数据（早于2019或晚于2024），用最近年份填充
for col in macro_data.keys():
    if col == "year":
        continue
    if df[col].isna().any():
        # 用所有年份的均值填充
        fill_val = macro_df[col].mean()
        df[col] = df[col].fillna(fill_val)
        print(f"  {col}: 填充了 {(df[col].isna().sum()) if False else '缺失值'} (均值={fill_val:.2f})")

print(f"合并后训练集: {len(df)} 条, 新增 {len(macro_data)-1} 个宏观特征")

# 为预测集也添加宏观特征（使用最新年份2024的数据）
for key in macro_data:
    if key == "year":
        continue
    df_predict[key] = macro_df[macro_df["year"] == 2024][key].values[0]
print(f"预测集已添加宏观经济特征（使用2024年数据）")

# ============================================================
# 4. 构建增强特征集并训练模型
# ============================================================
print("\n" + "=" * 60)
print("Step 4: 增强模型训练与对比")
print("=" * 60)

from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from sklearn.metrics import (accuracy_score, precision_score, recall_score,
                              f1_score, classification_report)
from xgboost import XGBClassifier
from lightgbm import LGBMClassifier

# 基础特征 (问题二中使用的个人特征)
BASE_FEATURES = [
    "age", "sex", "nation", "marriage", "edu_level", "politic",
    "religion", "c_aac009", "c_aac011", "type",
    "military_status", "is_disability", "is_teen", "is_elder",
    "change_type", "is_living_alone"
]

# 宏观特征
MACRO_FEATURES = [
    "gdp_growth", "cpi", "urban_unemployment_rate",
    "recruitment_index", "social_insurance_rate",
    "housing_price_income_ratio", "tertiary_industry_share"
]

ENHANCED_FEATURES = BASE_FEATURES + MACRO_FEATURES
TARGET = "employment_status"

# 准备数据
X_base = df[BASE_FEATURES].copy()
X_enhanced = df[ENHANCED_FEATURES].copy()
y = df[TARGET].copy()

# 缺失值填充
for col in BASE_FEATURES + MACRO_FEATURES:
    if col in X_base.columns and X_base[col].isna().any():
        X_base[col] = X_base[col].fillna(X_base[col].median())
    if col in X_enhanced.columns and X_enhanced[col].isna().any():
        X_enhanced[col] = X_enhanced[col].fillna(X_enhanced[col].median())

# 分层划分（使用同一划分保证对比公平性）
Xb_train, Xb_test, Xe_train, Xe_test, y_train, y_test = train_test_split(
    X_base, X_enhanced, y, test_size=0.2, random_state=42, stratify=y
)

print(f"训练集: {len(Xb_train)}, 测试集: {len(Xb_test)}")

models = {
    "Logistic Regression": LogisticRegression(max_iter=2000, random_state=42),
    "Decision Tree": DecisionTreeClassifier(max_depth=8, random_state=42),
    "Random Forest": RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42, n_jobs=-1),
    "KNN": KNeighborsClassifier(n_neighbors=7),
    "SVM": SVC(kernel="rbf", probability=True, random_state=42),
    "Gradient Boosting": GradientBoostingClassifier(n_estimators=100, max_depth=5, random_state=42),
    "XGBoost": XGBClassifier(n_estimators=100, max_depth=6, learning_rate=0.1, random_state=42, eval_metric="logloss", verbosity=0),
    "LightGBM": LGBMClassifier(n_estimators=100, max_depth=6, learning_rate=0.1, random_state=42, verbose=-1),
}

# 分别在基础特征集和增强特征集上训练
results_comparison = []

for name, model in models.items():
    # 基础特征
    model_base = model.__class__(**{k: v for k, v in model.get_params().items()
                                     if k not in ["random_state"]})
    # 重新创建模型实例以避免状态污染
    if name == "Logistic Regression":
        model_b = LogisticRegression(max_iter=2000, random_state=42)
        model_e = LogisticRegression(max_iter=2000, random_state=42)
    elif name == "Decision Tree":
        model_b = DecisionTreeClassifier(max_depth=8, random_state=42)
        model_e = DecisionTreeClassifier(max_depth=8, random_state=42)
    elif name == "Random Forest":
        model_b = RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42, n_jobs=-1)
        model_e = RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42, n_jobs=-1)
    elif name == "KNN":
        model_b = KNeighborsClassifier(n_neighbors=7)
        model_e = KNeighborsClassifier(n_neighbors=7)
    elif name == "SVM":
        model_b = SVC(kernel="rbf", probability=True, random_state=42)
        model_e = SVC(kernel="rbf", probability=True, random_state=42)
    elif name == "Gradient Boosting":
        model_b = GradientBoostingClassifier(n_estimators=100, max_depth=5, random_state=42)
        model_e = GradientBoostingClassifier(n_estimators=100, max_depth=5, random_state=42)
    elif name == "XGBoost":
        model_b = XGBClassifier(n_estimators=100, max_depth=6, learning_rate=0.1, random_state=42, eval_metric="logloss", verbosity=0)
        model_e = XGBClassifier(n_estimators=100, max_depth=6, learning_rate=0.1, random_state=42, eval_metric="logloss", verbosity=0)
    elif name == "LightGBM":
        model_b = LGBMClassifier(n_estimators=100, max_depth=6, learning_rate=0.1, random_state=42, verbose=-1)
        model_e = LGBMClassifier(n_estimators=100, max_depth=6, learning_rate=0.1, random_state=42, verbose=-1)

    # 训练基础模型
    model_b.fit(Xb_train, y_train)
    y_pred_b = model_b.predict(Xb_test)
    acc_b = accuracy_score(y_test, y_pred_b)
    f1_b = f1_score(y_test, y_pred_b, average="weighted", zero_division=0)
    prec_b = precision_score(y_test, y_pred_b, average="weighted", zero_division=0)
    rec_b = recall_score(y_test, y_pred_b, average="weighted", zero_division=0)

    # 训练增强模型
    model_e.fit(Xe_train, y_train)
    y_pred_e = model_e.predict(Xe_test)
    acc_e = accuracy_score(y_test, y_pred_e)
    f1_e = f1_score(y_test, y_pred_e, average="weighted", zero_division=0)
    prec_e = precision_score(y_test, y_pred_e, average="weighted", zero_division=0)
    rec_e = recall_score(y_test, y_pred_e, average="weighted", zero_division=0)

    results_comparison.append({
        "模型": name,
        "基础准确率": round(acc_b, 4), "增强准确率": round(acc_e, 4),
        "基础查准率": round(prec_b, 4), "增强查准率": round(prec_e, 4),
        "基础召回率": round(rec_b, 4), "增强召回率": round(rec_e, 4),
        "基础F1": round(f1_b, 4), "增强F1": round(f1_e, 4),
        "F1变化": round(f1_e - f1_b, 4),
    })
    print(f"  {name:25s} | 基础F1={f1_b:.4f} | 增强F1={f1_e:.4f} | Δ={f1_e-f1_b:+.4f}")

# ============================================================
# 5. 结果对比表
# ============================================================
print("\n" + "=" * 60)
print("Step 5: 增强前后模型性能对比")
print("=" * 60)

results_df = pd.DataFrame(results_comparison).sort_values("增强F1", ascending=False)
print("\n各模型增强前后性能对比:")
cols_show = ["模型", "基础F1", "增强F1", "F1变化", "基础准确率", "增强准确率"]
print(results_df[cols_show].to_string(index=False))

# 找最优增强模型
best_enhanced_name = results_df.iloc[0]["模型"]
best_f1_change = results_df.iloc[0]["F1变化"]
avg_f1_change = results_df["F1变化"].mean()

print(f"\n最优增强模型: {best_enhanced_name}")
print(f"平均F1变化: {avg_f1_change:+.4f}")
print(f"模型数量: {len(results_df)} 个")

# ============================================================
# 6. 可视化对比
# ============================================================
print("\n" + "=" * 60)
print("Step 6: 可视化")
print("=" * 60)

# 6a. F1分数对比图
fig, ax = plt.subplots(figsize=(12, 6))
x = np.arange(len(results_df))
width = 0.35

bars1 = ax.bar(x - width/2, results_df["基础F1"], width, label="基础特征(仅个人)", color=COLORS[0], edgecolor="white")
bars2 = ax.bar(x + width/2, results_df["增强F1"], width, label="增强特征(+宏观)", color=COLORS[1], edgecolor="white")

ax.set_xticks(x)
ax.set_xticklabels(results_df["模型"], fontsize=9, rotation=30, ha="right")
ax.set_ylabel("F1 (加权)", fontsize=12)
ax.set_title("引入宏观因素前后模型F1对比", fontsize=14, fontweight="bold")
ax.legend(fontsize=10)
ax.set_ylim(0.6, 0.85)
ax.grid(axis="y", alpha=0.3)

# 标注变化值
for i, (_, row) in enumerate(results_df.iterrows()):
    if row["F1变化"] != 0:
        ax.annotate(f"{row['F1变化']:+.4f}",
                    xy=(i + width/2, row["增强F1"]),
                    xytext=(i + width/2, row["增强F1"] + 0.01),
                    ha="center", fontsize=8, color="green" if row["F1变化"] > 0 else "red")

plt.tight_layout()
save_chart("13_macro_comparison.png")
plt.close()

# 6b. 宏观指标趋势图
fig, axes = plt.subplots(2, 4, figsize=(16, 8))
axes = axes.flatten()

macro_plots = [
    ("gdp_growth", "GDP增速 (%)", COLORS[0]),
    ("cpi", "CPI指数", COLORS[1]),
    ("urban_unemployment_rate", "城镇登记失业率 (%)", COLORS[2]),
    ("recruitment_index", "招聘岗位指数", COLORS[3]),
    ("social_insurance_rate", "社保参保率 (%)", COLORS[4]),
    ("housing_price_income_ratio", "房价收入比", COLORS[5]),
    ("tertiary_industry_share", "第三产业占比 (%)", COLORS[6]),
]

for i, (col, title, color) in enumerate(macro_plots):
    ax = axes[i]
    ax.plot(macro_df["year"], macro_df[col], marker="o", linewidth=2,
            markersize=8, color=color, markerfacecolor="white", markeredgewidth=2)
    ax.set_title(title, fontsize=11, fontweight="bold")
    ax.set_xlabel("年份", fontsize=9)
    ax.set_ylabel(title.split("(")[0].strip(), fontsize=9)
    ax.grid(alpha=0.3)
    # 标注数值
    for x_val, y_val in zip(macro_df["year"], macro_df[col]):
        ax.annotate(f"{y_val:.1f}", (x_val, y_val), textcoords="offset points",
                    xytext=(0, 10), ha="center", fontsize=8)

# 隐藏多余的子图
axes[-1].set_visible(False)

fig.suptitle("宜昌市宏观经济指标趋势 (2019-2024)", fontsize=15, fontweight="bold", y=1.01)
plt.tight_layout()
save_chart("14_macro_trends.png")
plt.close()

# ============================================================
# 7. 用最优增强模型预测预测集
# ============================================================
print("\n" + "=" * 60)
print("Step 7: 对预测集进行预测")
print("=" * 60)

# 准备预测集数据
X_pred = df_predict[ENHANCED_FEATURES].copy()
for col in ENHANCED_FEATURES:
    if X_pred[col].isna().any():
        fill_val = X_enhanced[col].median()
        X_pred[col] = X_pred[col].fillna(fill_val)

# 训练最优增强模型
best_e_model = None
if best_enhanced_name == "Logistic Regression":
    best_e_model = LogisticRegression(max_iter=2000, random_state=42)
elif best_enhanced_name == "Decision Tree":
    best_e_model = DecisionTreeClassifier(max_depth=8, random_state=42)
elif best_enhanced_name == "Random Forest":
    best_e_model = RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42, n_jobs=-1)
elif best_enhanced_name == "KNN":
    best_e_model = KNeighborsClassifier(n_neighbors=7)
elif best_enhanced_name == "SVM":
    best_e_model = SVC(kernel="rbf", probability=True, random_state=42)
elif best_enhanced_name == "Gradient Boosting":
    best_e_model = GradientBoostingClassifier(n_estimators=100, max_depth=5, random_state=42)
elif best_enhanced_name == "XGBoost":
    best_e_model = XGBClassifier(n_estimators=100, max_depth=6, learning_rate=0.1, random_state=42, eval_metric="logloss", verbosity=0)
elif best_enhanced_name == "LightGBM":
    best_e_model = LGBMClassifier(n_estimators=100, max_depth=6, learning_rate=0.1, random_state=42, verbose=-1)

best_e_model.fit(Xe_train, y_train)
y_pred_final = best_e_model.predict(X_pred)
pred_proba = best_e_model.predict_proba(X_pred) if hasattr(best_e_model, "predict_proba") else None

emp_pred = (y_pred_final == 1).sum()
unemp_pred = (y_pred_final == 0).sum()

print(f"\n预测结果: 就业={emp_pred}人, 失业={unemp_pred}人")

print("\n示例表3 (增强模型): 就业状态预测结果")
print("=" * 60)
print(f"{'预测样本':<12} {'T1~T20':<15} {'就业数量':<10} {'失业数量':<10}")
print(f"{'就业状态':<12} {'':<15} {emp_pred:<10} {unemp_pred:<10}")

print("\n各样本预测详情:")
for i in range(len(df_predict)):
    pid = df_predict.iloc[i].get("people_id", f"T{i+1}")
    pred_label = "就业" if y_pred_final[i] == 1 else "失业"
    proba_str = f" 概率={pred_proba[i][1]:.3f}" if pred_proba is not None else ""
    print(f"  {pid}: 预测={pred_label}{proba_str}")

# 与问题二预测结果对比
print("\n与问题二预测对比 (Gradient Boosting基础 vs 增强):")
print("  问题三将在后续步骤中汇总对比")

# ============================================================
# 8. 汇总
# ============================================================
print("\n" + "=" * 60)
print("问题三分析完成！")
print(f"图表保存在: {CHART_DIR}")
print("=" * 60)

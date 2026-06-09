"""
问题二：就业状态预测
多模型对比 + 特征重要性 + 预测集预测
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

COLOR_PALETTE = ["#4472C4", "#ED7D31", "#A5A5A5", "#FFC000", "#5B9BD5",
                 "#70AD47", "#264478", "#9B59B6"]


def save_chart(filename, dpi=150):
    path = os.path.join(CHART_DIR, filename)
    plt.savefig(path, dpi=dpi, bbox_inches="tight", facecolor="white")
    print(f"  已保存: {filename}")


# ============================================================
# 1. 加载数据 + 特征选取
# ============================================================
print("=" * 60)
print("Step 1: 加载数据 & 特征选取")
print("=" * 60)

DATA_PATH = os.path.join(SCRIPT_DIR, "..", "数据预处理", "train_clean.csv")
PREDICT_PATH = os.path.join(SCRIPT_DIR, "..", "数据预处理", "predict_clean.csv")

df = pd.read_csv(DATA_PATH)
df_predict = pd.read_csv(PREDICT_PATH)
print(f"训练集: {len(df)} 条")
print(f"预测集: {len(df_predict)} 条")

# 仅使用个人基本信息特征 (预测集也有的列)
FEATURES = [
    "age", "sex", "nation", "marriage", "edu_level", "politic",
    "religion", "c_aac009", "c_aac011", "type",
    "military_status", "is_disability", "is_teen", "is_elder",
    "change_type", "is_living_alone"
]
TARGET = "employment_status"

# 确保所有特征为数值类型
for col in FEATURES:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    if col in df_predict.columns:
        df_predict[col] = pd.to_numeric(df_predict[col], errors="coerce")

# 检查特征完整性
missing_in_predict = [c for c in FEATURES if c not in df_predict.columns]
if missing_in_predict:
    print(f"WARNING: 预测集缺失特征: {missing_in_predict}")

X = df[FEATURES].copy()
y = df[TARGET].copy()

# 缺失值填充（用中位数/众数）
for col in FEATURES:
    if X[col].isna().any():
        fill_val = X[col].median() if X[col].dtype in ["float64", "int64"] else X[col].mode()[0]
        X[col] = X[col].fillna(fill_val)

X_pred = df_predict[FEATURES].copy()
for col in FEATURES:
    if X_pred[col].isna().any():
        fill_val = X_pred[col].median() if X_pred[col].dtype in ["float64", "int64"] else X_pred[col].mode()[0]
        X_pred[col] = X_pred[col].fillna(fill_val)

print(f"特征数: {len(FEATURES)}")
print(f"标签分布: 就业={y.sum()}, 失业={len(y) - y.sum()}")

# ============================================================
# 2. 数据划分
# ============================================================
print("\n" + "=" * 60)
print("Step 2: 数据划分")
print("=" * 60)

from sklearn.model_selection import train_test_split

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)
print(f"训练集: {len(X_train)}, 测试集: {len(X_test)}")
print(f"训练集标签分布: 就业={y_train.sum()}, 失业={len(y_train) - y_train.sum()}")
print(f"测试集标签分布: 就业={y_test.sum()}, 失业={len(y_test) - y_test.sum()}")

# ============================================================
# 3. 构建多个模型
# ============================================================
print("\n" + "=" * 60)
print("Step 3: 模型训练与对比")
print("=" * 60)

from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from sklearn.metrics import (accuracy_score, precision_score, recall_score,
                              f1_score, classification_report, roc_auc_score)

# 尝试导入XGBoost和LightGBM
try:
    from xgboost import XGBClassifier
    HAS_XGB = True
except ImportError:
    HAS_XGB = False
    print("XGBoost 未安装")

try:
    from lightgbm import LGBMClassifier
    HAS_LGB = True
except ImportError:
    HAS_LGB = False
    print("LightGBM 未安装")

models = {
    "Logistic Regression": LogisticRegression(max_iter=2000, random_state=42),
    "Decision Tree": DecisionTreeClassifier(max_depth=8, random_state=42),
    "Random Forest": RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42, n_jobs=-1),
    "KNN": KNeighborsClassifier(n_neighbors=7),
    "SVM": SVC(kernel="rbf", probability=True, random_state=42),
    "Gradient Boosting": GradientBoostingClassifier(n_estimators=100, max_depth=5, random_state=42),
}

if HAS_XGB:
    models["XGBoost"] = XGBClassifier(n_estimators=100, max_depth=6, learning_rate=0.1,
                                       random_state=42, eval_metric="logloss", verbosity=0)
if HAS_LGB:
    models["LightGBM"] = LGBMClassifier(n_estimators=100, max_depth=6, learning_rate=0.1,
                                         random_state=42, verbose=-1)

# 训练和评估
results = []
for name, model in models.items():
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)

    acc = accuracy_score(y_test, y_pred)
    prec = precision_score(y_test, y_pred, average="weighted", zero_division=0)
    rec = recall_score(y_test, y_pred, average="weighted", zero_division=0)
    f1 = f1_score(y_test, y_pred, average="weighted", zero_division=0)

    # 对失业类别的召回率（更重要）
    unemp_recall = recall_score(y_test, y_pred, pos_label=0, zero_division=0)

    results.append({
        "模型": name,
        "准确率": round(acc, 4),
        "查准率(加权)": round(prec, 4),
        "召回率(加权)": round(rec, 4),
        "F1(加权)": round(f1, 4),
        "失业召回率": round(unemp_recall, 4),
    })
    print(f"  {name:25s} | Acc={acc:.4f} | F1={f1:.4f} | 失业召回={unemp_recall:.4f}")

# ============================================================
# 4. 结果表格
# ============================================================
print("\n" + "=" * 60)
print("示例表2: 评价指标结果")
print("=" * 60)

results_df = pd.DataFrame(results).sort_values("F1(加权)", ascending=False)
print(results_df.to_string(index=False))

# 找最优模型
best_model_name = results_df.iloc[0]["模型"]
best_model = models[best_model_name]
print(f"\n最优模型: {best_model_name}")

# ============================================================
# 5. 特征重要性
# ============================================================
print("\n" + "=" * 60)
print("Step 5: 特征重要性分析")
print("=" * 60)

# 尝试从最优模型中获取特征重要性
feature_importance = None
if hasattr(best_model, "feature_importances_"):
    feature_importance = best_model.feature_importances_
elif best_model_name == "Logistic Regression":
    feature_importance = np.abs(best_model.coef_[0])
elif best_model_name == "SVM" and hasattr(best_model, "coef_"):
    feature_importance = np.abs(best_model.coef_[0])

if feature_importance is not None:
    fi_df = pd.DataFrame({
        "特征": FEATURES,
        "重要性": feature_importance
    }).sort_values("重要性", ascending=True)

    # 特征中文名映射
    feature_names_cn = {
        "age": "年龄", "sex": "性别", "nation": "民族",
        "marriage": "婚姻状态", "edu_level": "教育程度",
        "politic": "政治面貌", "religion": "宗教信仰",
        "c_aac009": "户口性质", "c_aac011": "文化程度",
        "type": "人口类型", "military_status": "兵役状态",
        "is_disability": "是否残疾", "is_teen": "是否青少年",
        "is_elder": "是否老年人", "change_type": "变动类型",
        "is_living_alone": "是否独居"
    }
    fi_df["特征名"] = fi_df["特征"].map(feature_names_cn)

    print("特征重要性排序:")
    for _, row in fi_df.iterrows():
        print(f"  {row['特征名']:10s} ({row['特征']:20s}): {row['重要性']:.4f}")

    # 条形图
    fig, ax = plt.subplots(figsize=(10, 6))
    top_n = min(16, len(fi_df))
    fi_plot = fi_df.tail(top_n)
    bars = ax.barh(range(len(fi_plot)), fi_plot["重要性"].values,
                   color=[COLOR_PALETTE[i % len(COLOR_PALETTE)] for i in range(len(fi_plot))],
                   edgecolor="white")
    ax.set_yticks(range(len(fi_plot)))
    ax.set_yticklabels(fi_plot["特征名"].values, fontsize=10)
    ax.set_xlabel("重要性", fontsize=12)
    ax.set_title(f"特征重要性排序 ({best_model_name})", fontsize=14, fontweight="bold")
    for bar, val in zip(bars, fi_plot["重要性"].values):
        ax.text(bar.get_width() + 0.001, bar.get_y() + bar.get_height()/2,
                f"{val:.4f}", va="center", fontsize=9)

    plt.tight_layout()
    save_chart("10_feature_importance.png")
    plt.close()
else:
    print(f"  {best_model_name} 不支持直接获取特征重要性")

# ============================================================
# 6. 最佳模型评估详情
# ============================================================
print("\n" + "=" * 60)
print("Step 6: 最佳模型详细评估")
print("=" * 60)

y_pred_best = best_model.predict(X_test)
print(f"\n{best_model_name} 详细分类报告:")
print(classification_report(y_test, y_pred_best, target_names=["失业", "就业"],
                            zero_division=0))

# 混淆矩阵热力图
from sklearn.metrics import confusion_matrix
cm = confusion_matrix(y_test, y_pred_best)

fig, ax = plt.subplots(figsize=(6, 5))
sns_heatmap = __import__("seaborn")
sns_heatmap.heatmap(cm, annot=True, fmt="d", cmap="Blues", ax=ax,
                    xticklabels=["失业", "就业"], yticklabels=["失业", "就业"],
                    annot_kws={"fontsize": 16})
ax.set_xlabel("预测值", fontsize=12)
ax.set_ylabel("真实值", fontsize=12)
ax.set_title(f"混淆矩阵 ({best_model_name})", fontsize=14, fontweight="bold")

plt.tight_layout()
save_chart("11_confusion_matrix.png")
plt.close()

# ============================================================
# 7. 预测集预测
# ============================================================
print("\n" + "=" * 60)
print("Step 7: 预测集预测")
print("=" * 60)

X_pred_clean = X_pred.copy()
# 确保特征列顺序与训练一致
X_pred_clean = X_pred_clean[FEATURES]

# 填充缺失值
for col in FEATURES:
    if X_pred_clean[col].isna().any():
        X_pred_clean[col] = X_pred_clean[col].fillna(X[col].median() if X[col].dtype in ["float64", "int64"] else X[col].mode()[0])

y_pred_final = best_model.predict(X_pred_clean)
pred_proba = best_model.predict_proba(X_pred_clean) if hasattr(best_model, "predict_proba") else None

# 组装预测结果
df_predict["predicted_status"] = y_pred_final
emp_pred = (y_pred_final == 1).sum()
unemp_pred = (y_pred_final == 0).sum()

# 如果有真实标签（预测列），计算准确率
if "预测" in df_predict.columns:
    true_labels = pd.to_numeric(df_predict["预测"], errors="coerce")
    pred_acc = (true_labels == y_pred_final).sum() / len(true_labels)
    print(f"预测集真实标签准确率: {pred_acc:.4f}")

print(f"\n预测结果: 就业={emp_pred}人, 失业={unemp_pred}人")

# 示例表3格式
print("\n示例表3: 就业状态预测结果")
print("=" * 60)
print(f"{'预测样本':<12} {'T1~T20':<15} {'就业数量':<10} {'失业数量':<10}")
print(f"{'就业状态':<12} {'':<15} {emp_pred:<10} {unemp_pred:<10}")
print(f"{'小计':<12} {'':<15} {emp_pred+unemp_pred:<10}")

print("\n各样本预测详情:")
for i, (idx, row) in enumerate(df_predict.iterrows()):
    people_id = row.get("people_id", f"T{i+1}")
    pred_label = "就业" if row["predicted_status"] == 1 else "失业"
    true_label = ""
    if "预测" in df_predict.columns and pd.notna(row.get("预测")):
        true_label = f" 真实={int(row['预测'])}"
    proba_str = ""
    if pred_proba is not None:
        proba_str = f" 概率={pred_proba[i][1]:.3f}"
    print(f"  {people_id}: 预测={pred_label}{true_label}{proba_str}")

# ============================================================
# 8. 模型对比柱状图
# ============================================================
print("\n" + "=" * 60)
print("Step 8: 模型对比可视化")
print("=" * 60)

fig, ax = plt.subplots(figsize=(12, 6))
metrics = ["准确率", "查准率(加权)", "召回率(加权)", "F1(加权)"]
plot_data = results_df.head(8)  # 取前8个模型

x = np.arange(len(metrics))
width = 0.1
n_models = len(plot_data)

for i, (_, row) in enumerate(plot_data.iterrows()):
    vals = [row[m] for m in metrics]
    offset = (i - n_models / 2 + 0.5) * width
    ax.bar(x + offset, vals, width, label=row["模型"], edgecolor="white", alpha=0.85)

ax.set_xticks(x)
ax.set_xticklabels(metrics, fontsize=11)
ax.set_ylabel("分数", fontsize=12)
ax.set_title("各模型评价指标对比", fontsize=14, fontweight="bold")
ax.legend(loc="lower right", fontsize=8, ncol=2)
ax.set_ylim(0, 1)
ax.grid(axis="y", alpha=0.3)

plt.tight_layout()
save_chart("12_model_comparison.png")
plt.close()

# ============================================================
# 汇总
# ============================================================
print("\n" + "=" * 60)
print("问题二分析完成！")
print(f"最优模型: {best_model_name}")
print(f"图表保存在: {CHART_DIR}")
print(f"共生成 3 张图表")
print("=" * 60)

"""
问题二：就业状态预测 (Skill增强版)
math-modeling + 类别不平衡处理 + 交叉验证 + 超参数调优
"""
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
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
    print(f"  -> {fname}")


# ============================================================
# 1. 加载数据
# ============================================================
print("Step 1: 加载数据")
df = pd.read_csv(os.path.join(SCRIPT_DIR, "..", "数据预处理", "train_clean.csv"))
df_pred = pd.read_csv(os.path.join(SCRIPT_DIR, "..", "数据预处理", "predict_clean.csv"))

FEATURES = [
    "age", "sex", "nation", "marriage", "edu_level", "politic",
    "religion", "c_aac009", "c_aac011", "type",
    "military_status", "is_disability", "is_teen", "is_elder",
    "change_type", "is_living_alone"
]
TARGET = "employment_status"

X = df[FEATURES].apply(pd.to_numeric, errors="coerce")
y = df[TARGET]
X_pred = df_pred[FEATURES].apply(pd.to_numeric, errors="coerce")

# 缺失值填充
for col in FEATURES:
    fill_v = X[col].median() if X[col].dtype in ["float64", "int64"] else X[col].mode()[0]
    X[col] = X[col].fillna(fill_v)
    if col in X_pred.columns:
        X_pred[col] = X_pred[col].fillna(fill_v)

print(f"训练集: {X.shape}, 就业={y.sum()}, 失业={len(y)-y.sum()}")
print(f"类别比: {y.sum()/(len(y)-y.sum()):.1f}:1 → 启用class_weight='balanced'")

# ============================================================
# 2. 分层5折交叉验证 (替代单次划分)
# ============================================================
print("\nStep 2: 分层5折交叉验证")

from sklearn.model_selection import StratifiedKFold, cross_validate, GridSearchCV
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from xgboost import XGBClassifier
from lightgbm import LGBMClassifier
from sklearn.metrics import (make_scorer, accuracy_score, precision_score,
                              recall_score, f1_score, roc_auc_score)

cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=RANDOM_STATE)

scoring = {
    "accuracy": "accuracy",
    "precision_weighted": make_scorer(precision_score, average="weighted", zero_division=0),
    "recall_weighted": make_scorer(recall_score, average="weighted", zero_division=0),
    "f1_weighted": make_scorer(f1_score, average="weighted", zero_division=0),
    "recall_unemp": make_scorer(recall_score, pos_label=0, zero_division=0),
    "roc_auc": make_scorer(roc_auc_score, response_method="predict_proba"),
}

# ============================================================
# 3. 模型定义 (全部启用class_weight)
# ============================================================
print("Step 3: 模型训练 (5折CV + class_weight)")

models = {
    "Logistic Regression": LogisticRegression(max_iter=2000, class_weight="balanced", random_state=RANDOM_STATE),
    "Decision Tree": DecisionTreeClassifier(max_depth=8, class_weight="balanced", random_state=RANDOM_STATE),
    "Random Forest": RandomForestClassifier(n_estimators=100, max_depth=10, class_weight="balanced", random_state=RANDOM_STATE, n_jobs=-1),
    "KNN": KNeighborsClassifier(n_neighbors=7),
    "Gradient Boosting": GradientBoostingClassifier(n_estimators=100, max_depth=5, random_state=RANDOM_STATE),
    "XGBoost": XGBClassifier(n_estimators=100, max_depth=6, learning_rate=0.1, scale_pos_weight=3.4, random_state=RANDOM_STATE, eval_metric="logloss", verbosity=0),
    "LightGBM": LGBMClassifier(n_estimators=100, max_depth=6, learning_rate=0.1, class_weight="balanced", random_state=RANDOM_STATE, verbose=-1),
}

cv_results = {}
for name, model in models.items():
    # SVM 单独训练(慢, 只用3折)
    if name == "SVM":
        continue  # SVM太慢，跳过CV，后面单独train_test_split评估

    scores = cross_validate(model, X, y, cv=cv, scoring=scoring, n_jobs=-1, return_train_score=False)
    cv_results[name] = {k: (np.mean(v), np.std(v)) for k, v in scores.items() if k.startswith("test_")}
    print(f"  {name:25s} | F1={scores['test_f1_weighted'].mean():.4f}+/-{scores['test_f1_weighted'].std():.4f} | "
          f"失业召回={scores['test_recall_unemp'].mean():.4f} | AUC={scores['test_roc_auc'].mean():.4f}")

# SVM单独评估 (train_test_split)
from sklearn.model_selection import train_test_split
X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.2, stratify=y, random_state=RANDOM_STATE)
svm = SVC(kernel="rbf", class_weight="balanced", probability=True, random_state=RANDOM_STATE)
svm.fit(X_tr, y_tr)
y_svm = svm.predict(X_te)
cv_results["SVM"] = {
    "test_accuracy": (accuracy_score(y_te, y_svm), 0),
    "test_f1_weighted": (f1_score(y_te, y_svm, average="weighted", zero_division=0), 0),
    "test_recall_unemp": (recall_score(y_te, y_svm, pos_label=0, zero_division=0), 0),
    "test_roc_auc": (roc_auc_score(y_te, svm.predict_proba(X_te)[:, 1]), 0),
}

# ============================================================
# 4. 结果汇总
# ============================================================
print("\n" + "=" * 60)
print("示例表2: 评价指标结果 (5折CV均值 ± 标准差)")
print("=" * 60)

table_rows = []
for name in ["Gradient Boosting", "XGBoost", "Random Forest", "LightGBM",
             "Logistic Regression", "Decision Tree", "KNN", "SVM"]:
    if name not in cv_results:
        continue
    r = cv_results[name]
    table_rows.append({
        "模型": name,
        "准确率": f"{r['test_accuracy'][0]:.4f}±{r['test_accuracy'][1]:.4f}",
        "F1(加权)": f"{r['test_f1_weighted'][0]:.4f}±{r['test_f1_weighted'][1]:.4f}",
        "失业召回率": f"{r['test_recall_unemp'][0]:.4f}±{r['test_recall_unemp'][1]:.4f}",
        "ROC-AUC": f"{r['test_roc_auc'][0]:.4f}±{r['test_roc_auc'][1]:.4f}",
    })

results_df = pd.DataFrame(table_rows).sort_values("F1(加权)", ascending=False)
print(results_df.to_string(index=False))

# 找最优模型
best_name = results_df.iloc[0]["模型"]
print(f"\n最优模型: {best_name}")

# ============================================================
# 5. 最优模型GridSearchCV调优
# ============================================================
print(f"\nStep 5: {best_name} 超参数调优 (GridSearchCV)")

if best_name == "Random Forest":
    param_grid = {
        "n_estimators": [100, 200],
        "max_depth": [8, 10, 12],
        "min_samples_split": [2, 5],
        "class_weight": ["balanced", "balanced_subsample"],
    }
    base_model = RandomForestClassifier(random_state=RANDOM_STATE, n_jobs=-1)
elif best_name == "XGBoost":
    param_grid = {
        "n_estimators": [100, 200],
        "max_depth": [4, 6, 8],
        "learning_rate": [0.05, 0.1],
        "scale_pos_weight": [3.0, 3.4, 4.0],
    }
    base_model = XGBClassifier(random_state=RANDOM_STATE, eval_metric="logloss", verbosity=0)
elif best_name == "Gradient Boosting":
    param_grid = {
        "n_estimators": [100, 200],
        "max_depth": [3, 5, 7],
        "learning_rate": [0.05, 0.1],
    }
    base_model = GradientBoostingClassifier(random_state=RANDOM_STATE)
elif best_name == "LightGBM":
    param_grid = {
        "n_estimators": [100, 200],
        "max_depth": [4, 6, 8],
        "learning_rate": [0.05, 0.1],
        "class_weight": ["balanced", None],
    }
    base_model = LGBMClassifier(random_state=RANDOM_STATE, verbose=-1)
else:
    # 逻辑回归或KNN: 简单网格
    param_grid = {"C": [0.1, 1, 10]} if best_name == "Logistic Regression" else {"n_neighbors": [5, 7, 9]}
    base_model = LogisticRegression(max_iter=2000, class_weight="balanced", random_state=RANDOM_STATE) \
        if best_name == "Logistic Regression" else KNeighborsClassifier()

grid = GridSearchCV(base_model, param_grid, cv=3, scoring="f1_weighted", n_jobs=-1, verbose=0)
grid.fit(X, y)
print(f"  最佳参数: {grid.best_params_}")
print(f"  最佳CV F1: {grid.best_score_:.4f}")

best_model = grid.best_estimator_

# ============================================================
# 6. 最终评估 (train_test_split)
# ============================================================
print("\nStep 6: 最终评估")

best_model.fit(X_tr, y_tr)
y_pred = best_model.predict(X_te)
y_proba = best_model.predict_proba(X_te)[:, 1]

from sklearn.metrics import classification_report, confusion_matrix
print(f"\n{best_name}(调优后) 分类报告:")
print(classification_report(y_te, y_pred, target_names=["失业", "就业"], zero_division=0))

# 混淆矩阵
cm = confusion_matrix(y_te, y_pred)
fig, ax = plt.subplots(figsize=(6, 5))
sns.heatmap(cm, annot=True, fmt="d", cmap="Blues", ax=ax,
            xticklabels=["失业", "就业"], yticklabels=["失业", "就业"],
            annot_kws={"fontsize": 16})
ax.set_xlabel("预测值"); ax.set_ylabel("真实值")
ax.set_title(f"混淆矩阵 ({best_name}, 调优后)", fontweight="bold")
plt.tight_layout(); save_chart("01_confusion_matrix.png")

# ROC曲线
from sklearn.metrics import RocCurveDisplay
fig, ax = plt.subplots(figsize=(6, 5))
RocCurveDisplay.from_estimator(best_model, X_te, y_te, ax=ax, color=PALETTE[0], lw=2)
ax.plot([0, 1], [0, 1], "k--", lw=1, alpha=0.5)
ax.set_title(f"ROC曲线 ({best_name}, AUC={roc_auc_score(y_te, y_proba):.4f})", fontweight="bold")
plt.tight_layout(); save_chart("02_roc_curve.png")

# ============================================================
# 7. 特征重要性
# ============================================================
print("\nStep 7: 特征重要性")

# KNN无feature_importances_，用Gradient Boosting(有真正importances且CV表现好)来展示
gb_for_imp = GradientBoostingClassifier(n_estimators=100, max_depth=5, random_state=RANDOM_STATE)
gb_for_imp.fit(X, y)
imp = gb_for_imp.feature_importances_

feat_cn = {
    "age": "年龄", "sex": "性别", "nation": "民族", "marriage": "婚姻状态",
    "edu_level": "教育程度", "politic": "政治面貌", "religion": "宗教信仰",
    "c_aac009": "户口性质", "c_aac011": "文化程度", "type": "人口类型",
    "military_status": "兵役状态", "is_disability": "是否残疾",
    "is_teen": "是否青少年", "is_elder": "是否老年人",
    "change_type": "变动类型", "is_living_alone": "是否独居",
}

fi = pd.DataFrame({"feat": FEATURES, "imp": imp}).sort_values("imp", ascending=True)
fi["name"] = fi["feat"].map(feat_cn)

fig, ax = plt.subplots(figsize=(10, 6))
bars = ax.barh(range(len(fi)), fi["imp"].values,
               color=[PALETTE[i % len(PALETTE)] for i in range(len(fi))], edgecolor="white")
ax.set_yticks(range(len(fi))); ax.set_yticklabels(fi["name"].values, fontsize=10)
ax.set_xlabel("重要性", fontsize=12)
ax.set_title("特征重要性 (Gradient Boosting)", fontweight="bold")
for b, v in zip(bars, fi["imp"].values):
    ax.text(b.get_width() + 0.001, b.get_y() + b.get_height()/2, f"{v:.4f}", va="center", fontsize=9)
plt.tight_layout(); save_chart("03_feature_importance.png")

# ============================================================
# 8. 模型对比图 (Prompt版 vs Skill版)
# ============================================================
print("\nStep 8: 模型对比图")

fig, ax = plt.subplots(figsize=(12, 6))

# 模型性能对比柱状图
fig, ax = plt.subplots(figsize=(12, 6))
names = list(cv_results.keys())
x = np.arange(len(names))
f1_vals = [cv_results[n]["test_f1_weighted"][0] for n in names]
ur_vals = [cv_results[n]["test_recall_unemp"][0] for n in names]

ax2 = ax.twinx()
b1 = ax.bar(x - 0.15, f1_vals, 0.3, label="F1(加权)", color=PALETTE[0], edgecolor="white")
b2 = ax2.bar(x + 0.15, ur_vals, 0.3, label="失业召回率", color=PALETTE[1], edgecolor="white")

ax.set_xticks(x); ax.set_xticklabels(names, fontsize=8, rotation=30, ha="right")
ax.set_ylabel("F1 分数", fontsize=12); ax.set_title("各模型F1与失业召回率对比 (5折CV)", fontweight="bold")
ax.legend(loc="upper left", fontsize=9)
ax2.legend(loc="upper right", fontsize=9)
ax.set_ylim(0, 1); ax.grid(axis="y", alpha=0.3)

plt.tight_layout(); save_chart("04_model_overview.png")

# ============================================================
# 9. 预测集预测
# ============================================================
print("\nStep 9: 预测集预测")

for col in FEATURES:
    if col in X_pred.columns and X_pred[col].isna().any():
        X_pred[col] = X_pred[col].fillna(X[col].median())

y_final = best_model.predict(X_pred)
emp_p, unemp_p = (y_final == 1).sum(), (y_final == 0).sum()
print(f"预测: 就业={emp_p}人, 失业={unemp_p}人")
print(f"\n示例表3 就业状态预测结果:")
print(f"{'预测样本':<12} {'T1~T20':<15} {'就业数量':<10} {'失业数量':<10}")
print(f"{'就业状态':<12} {'':<15} {emp_p:<10} {unemp_p:<10}")

proba = best_model.predict_proba(X_pred)[:, 1] if hasattr(best_model, "predict_proba") else None
for i in range(len(df_pred)):
    pid = df_pred.iloc[i].get("people_id", f"T{i+1}")
    label = "就业" if y_final[i] == 1 else "失业"
    p_str = f" p={proba[i]:.3f}" if proba is not None else ""
    print(f"  {pid}: {label}{p_str}")

# ============================================================
print("\n" + "=" * 60)
print("问题二 (Skill增强版) 完成!")
print(f"核心改进: class_weight平衡 | 5折CV | GridSearchCV | ROC-AUC | 失业召回率修复")
print("=" * 60)

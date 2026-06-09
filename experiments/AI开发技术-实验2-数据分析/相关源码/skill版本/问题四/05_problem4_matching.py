"""
问题四：人岗精准匹配 (Skill增强版)
岗位画像聚合 + 特征加权 + 多样性约束 + 行业覆盖优化
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

plt.rcParams["font.sans-serif"] = ["SimHei", "Microsoft YaHei", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False
PALETTE = ["#2B579A", "#E87722", "#6B6B6B", "#F4B400", "#4285F4",
           "#0F9D58", "#9C27B0", "#3F51B8"]


def save_chart(fname, dpi=150):
    plt.savefig(os.path.join(CHART_DIR, fname), dpi=dpi, bbox_inches="tight", facecolor="white")
    plt.close()


# ============================================================
# 1. 加载数据
# ============================================================
print("Step 1: 加载数据")
df = pd.read_csv(os.path.join(SCRIPT_DIR, "..", "数据预处理", "train_clean.csv"))
employed = df[df["employment_status"] == 1].copy()
unemployed = df[df["employment_status"] == 0].copy()
print(f"就业(岗位来源): {len(employed)}人, 失业(求职者): {len(unemployed)}人")

# ============================================================
# 2. 特征选择与加权 (Skill版: 多维+加权)
# ============================================================
print("\nStep 2: 构建特征画像 (技能加权)")

# 求职者特征 (12维, 比Prompt版多4维)
seeker_features = [
    "age", "sex", "marriage", "edu_level", "c_aac009",
    "c_aac011", "type", "nation", "is_disability",
    "profession_has_value", "is_living_alone", "change_type"
]

# 特征权重 (行业/技能 > 人口统计)
FEATURE_WEIGHTS = {
    "age": 1.0, "sex": 0.8, "marriage": 0.8, "edu_level": 1.5,
    "c_aac009": 1.2, "c_aac011": 1.5, "type": 1.0, "nation": 0.5,
    "is_disability": 1.2, "profession_has_value": 1.5,
    "is_living_alone": 0.8, "change_type": 0.5,
}

# ============================================================
# 3. 构建岗位画像 (聚合就业人员 → 去重岗位池)
# ============================================================
print("Step 3: 构建岗位画像池 (行业×地区聚合)")

# 用行业类别+地区作为岗位标识 (在split之前构建)
df["industry_category"] = df["industry_category"].fillna("Z")
df["region_code"] = df["c_aab299"].astype(str).str[:4]

# 重新提取employed (包含新增的region_code列)
employed = df[df["employment_status"] == 1].copy()
unemployed = df[df["employment_status"] == 0].copy()

# 创建岗位池: 每个行业×区域组合作为一个"岗位类型"
position_pool = employed.groupby(["industry_category", "region_code"], dropna=False).agg(
    **{f"{feat}_mean": (feat, "mean") for feat in seeker_features},
    position_count=("id", "count"),
    sample_company=("b_aab004", "first"),
).reset_index()

# 过滤样本量过小的岗位
position_pool = position_pool[position_pool["position_count"] >= 3].reset_index(drop=True)
print(f"岗位池规模: {len(position_pool)} 个岗位类型 (去重后)")

# ============================================================
# 4. 特征向量构建 + 加权
# ============================================================
print("Step 4: 特征向量化 + 加权")

from sklearn.preprocessing import MinMaxScaler

# 求职者向量
seeker_data = unemployed[seeker_features].copy()
for col in seeker_features:
    seeker_data[col] = pd.to_numeric(seeker_data[col], errors="coerce")
seeker_data = seeker_data.fillna(0)

# 岗位向量
position_feat_cols = [f"{feat}_mean" for feat in seeker_features]
position_data = position_pool[position_feat_cols].copy()
position_data = position_data.fillna(0)

# 应用特征权重
weights_array = np.array([FEATURE_WEIGHTS[f] for f in seeker_features])
seeker_weighted = seeker_data.values * weights_array
position_weighted = position_data.values * weights_array

# MinMax标准化
scaler = MinMaxScaler()
all_data = np.vstack([seeker_weighted, position_weighted])
all_scaled = scaler.fit_transform(all_data)

seeker_vecs = all_scaled[:len(unemployed)]
position_vecs = all_scaled[len(unemployed):]

print(f"求职者向量: {seeker_vecs.shape}")
print(f"岗位向量: {position_vecs.shape}")

# ============================================================
# 5. 余弦相似度 + 多样性约束推荐
# ============================================================
print("Step 5: 余弦相似度匹配 + 多样性约束")

from sklearn.metrics.pairwise import cosine_similarity

sim_matrix = cosine_similarity(seeker_vecs, position_vecs)
print(f"相似度: 范围[{sim_matrix.min():.4f}, {sim_matrix.max():.4f}], 均值={sim_matrix.mean():.4f}")

K = 5

# 带多样性约束的推荐: Top-K中尽量覆盖不同行业
industry_map = {
    "A": "农/林/牧/渔", "B": "采矿", "C": "制造", "D": "电力/热力",
    "E": "建筑", "F": "批发/零售", "G": "交通运输", "H": "住宿/餐饮",
    "I": "信息技术", "J": "金融", "K": "房地产", "L": "租赁/商务",
    "M": "科研/技术", "N": "水利/环境", "O": "居民服务", "P": "教育",
    "Q": "卫生/社会", "R": "文化/体育", "S": "公共管理", "Z": "其他"
}

all_recommendations = []
for i in range(len(unemployed)):
    scores = sim_matrix[i]
    sorted_idx = np.argsort(-scores)

    # 多样性约束: Top-3不同行业, 其余按分数
    seen_industries = set()
    diverse_recs = []
    remaining = []

    for idx in sorted_idx:
        industry = position_pool.iloc[idx]["industry_category"]
        if industry not in seen_industries and len(diverse_recs) < 3:
            diverse_recs.append(idx)
            seen_industries.add(industry)
        else:
            remaining.append(idx)

    # 合并: 前3个多样化 + 剩余top分数补足到K
    final_recs = diverse_recs + remaining[:K - len(diverse_recs)]

    rec_jobs = []
    for k, pos_idx in enumerate(final_recs):
        row = position_pool.iloc[pos_idx]
        rec_jobs.append({
            "排名": k + 1,
            "行业代码": row["industry_category"],
            "行业": industry_map.get(row["industry_category"], "其他"),
            "单位参考": str(row["sample_company"])[:25] if pd.notna(row["sample_company"]) else "N/A",
            "相似度": round(scores[pos_idx], 4),
        })

    seeker_row = unemployed.iloc[i]
    all_recommendations.append({
        "求职者ID": seeker_row["id"],
        "年龄": seeker_row["age"],
        "学历": seeker_row["edu_label"] if pd.notna(seeker_row.get("edu_label")) else seeker_row["edu_level"],
        "性别": "男" if seeker_row["sex"] == 1 else "女",
        "推荐岗位": rec_jobs,
        "Top1相似度": rec_jobs[0]["相似度"],
        "Top5相似度": np.mean([r["相似度"] for r in rec_jobs]),
    })

# ============================================================
# 6. 结果展示
# ============================================================
print("\nStep 6: 推荐结果")

print("\n前10位求职者推荐:")
for rec in all_recommendations[:10]:
    print(f"\n  求职者 ID={rec['求职者ID']}, {rec['年龄']}岁, {rec['性别']}")
    for job in rec["推荐岗位"][:3]:
        print(f"    Top{job['排名']}: {job['行业']} | {job['单位参考']} | sim={job['相似度']:.4f}")

# ============================================================
# 7. 统计汇总
# ============================================================
print("\nStep 7: 统计汇总")

top1_scores = [r["Top1相似度"] for r in all_recommendations]
top5_scores = [r["Top5相似度"] for r in all_recommendations]

print(f"Top-1相似度: max={max(top1_scores):.4f}, min={min(top1_scores):.4f}, "
      f"mean={np.mean(top1_scores):.4f}, median={np.median(top1_scores):.4f}")
print(f"Top-5平均: {np.mean(top5_scores):.4f}")

# 相似度分布统计
bins = [0, 0.3, 0.5, 0.7, 0.85, 1.01]
labels = ["<0.3", "0.3-0.5", "0.5-0.7", "0.7-0.85", "0.85-1.0"]
sim_dist = pd.cut(top1_scores, bins=bins, labels=labels).value_counts()
print("\nTop-1相似度分布:")
for label in labels:
    cnt = sim_dist.get(label, 0)
    print(f"  {label}: {cnt}人 ({cnt/len(top1_scores)*100:.1f}%)")

# 行业覆盖
all_industries = []
for rec in all_recommendations:
    for job in rec["推荐岗位"]:
        all_industries.append(job["行业"])
from collections import Counter
ind_counter = Counter(all_industries)
print(f"\n推荐行业覆盖: {len(ind_counter)} 个行业类别")
print("Top10推荐行业:")
for ind, cnt in ind_counter.most_common(10):
    print(f"  {ind}: {cnt}次 ({cnt/len(all_industries)*100:.1f}%)")

# ============================================================
# 8. 可视化
# ============================================================
print("\nStep 8: 可视化")

fig, axes = plt.subplots(2, 2, figsize=(15, 12))

# 相似度分布
ax = axes[0, 0]
ax.hist(top1_scores, bins=30, color=PALETTE[0], edgecolor="white", alpha=0.85)
ax.axvline(np.mean(top1_scores), color="red", ls="--", lw=2, label=f"均值={np.mean(top1_scores):.4f}")
ax.axvline(np.median(top1_scores), color=PALETTE[1], ls="--", lw=2, label=f"中位={np.median(top1_scores):.4f}")
ax.set_xlabel("Top-1余弦相似度"); ax.set_ylabel("求职者人数")
ax.set_title("匹配相似度分布 (Skill增强版)", fontweight="bold")
ax.legend()

# 相似度分档
ax = axes[0, 1]
ax.pie(sim_dist.values, labels=sim_dist.index, autopct="%1.1f%%",
       colors=PALETTE[:5], explode=(0, 0, 0, 0, 0.05))
ax.set_title("Top-1相似度分档", fontweight="bold")

# 行业分布
ax = axes[1, 0]
top_ind = ind_counter.most_common(15)
ax.barh(range(len(top_ind)), [x[1] for x in top_ind], color=PALETTE[:len(top_ind)], edgecolor="white")
ax.set_yticks(range(len(top_ind)))
ax.set_yticklabels([x[0] for x in top_ind], fontsize=9)
ax.set_xlabel("推荐次数"); ax.set_title("推荐行业覆盖 (多样性约束)", fontweight="bold")
ax.invert_yaxis()

# 各排名相似度降幅
ax = axes[1, 1]
rank_avg = [np.mean([r["推荐岗位"][k]["相似度"] for r in all_recommendations]) for k in range(K)]
ax.plot(range(1, K+1), rank_avg, marker="o", lw=2, ms=10, color=PALETTE[0], markerfacecolor="white")
ax.set_xlabel("推荐排名"); ax.set_ylabel("平均相似度")
ax.set_title("Top-K相似度衰减曲线", fontweight="bold")
ax.set_xticks(range(1, K+1)); ax.grid(alpha=0.3)
for k, v in enumerate(rank_avg):
    ax.annotate(f"{v:.4f}", (k+1, v), textcoords="offset points", xytext=(0, 10), ha="center", fontsize=9)

plt.tight_layout()
save_chart("01_matching_analysis.png")

# ============================================================
# ============================================================
print("\n" + "=" * 60)
print("问题四 (Skill增强版) 完成!")
print(f"求职者: {len(unemployed)}人 | 岗位池: {len(position_pool)}个岗位类型")
print(f"核心改进: 岗位画像聚合 | 特征加权 | 多样性约束(3行业) | 区分度改善")
print(f"外部数据: 用人单位信息(赛题数据) | 行业分类(赛题行业代码表)")
print("=" * 60)

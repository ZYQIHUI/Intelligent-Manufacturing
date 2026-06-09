"""
问题四：人岗精准匹配
基于余弦相似度的多维匹配模型，为失业人员推荐岗位
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
print("Step 1: 加载数据")
print("=" * 60)

DATA_PATH = os.path.join(SCRIPT_DIR, "..", "数据预处理", "train_clean.csv")
df = pd.read_csv(DATA_PATH)
print(f"总样本: {len(df)}")

# 分离就业人员和失业人员
employed = df[df["employment_status"] == 1].copy()
unemployed = df[df["employment_status"] == 0].copy()
print(f"就业人员(岗位来源): {len(employed)} 人")
print(f"失业人员(求职者): {len(unemployed)} 人")

# ============================================================
# 2. 构建匹配特征
# ============================================================
print("\n" + "=" * 60)
print("Step 2: 构建匹配特征")
print("=" * 60)

# 求职者画像特征
seeker_features = [
    "age", "sex", "marriage", "edu_level", "c_aac009",
    "c_aac011", "type", "nation"
]

# 岗位画像特征 (从就业人员中提取)
position_features = [
    "industry_category",   # 行业大类(首字母)
]

# 共同特征用于编码
common_features = seeker_features

print(f"匹配维度: {len(seeker_features)}个求职者特征 + 行业信息")
print(f"求职者特征: {seeker_features}")

# ============================================================
# 3. 特征向量化
# ============================================================
print("\n" + "=" * 60)
print("Step 3: 特征编码与向量化")
print("=" * 60)

from sklearn.preprocessing import MinMaxScaler, LabelEncoder
from sklearn.metrics.pairwise import cosine_similarity


def build_feature_vectors(df_seekers, df_positions, seeker_cols):
    """
    构建求职者和岗位的特征向量
    将两个群体用相同编码方式映射到同一特征空间
    """
    # 合并两个数据集以统一编码
    df_seekers = df_seekers.copy()
    df_positions = df_positions.copy()

    # 标记来源
    df_seekers["_source"] = "seeker"
    df_positions["_source"] = "position"

    combined = pd.concat([df_seekers, df_positions], ignore_index=True)

    # 对每个特征进行编码
    encoded_cols = []
    for col in seeker_cols:
        if col not in combined.columns:
            continue

        # Convert to numeric if possible
        combined[col] = pd.to_numeric(combined[col], errors="coerce")

        # Fill NaN with median for numeric columns
        if combined[col].dtype in ["float64", "int64"]:
            combined[col] = combined[col].fillna(combined[col].median())
            encoded_cols.append(col)

    # 添加行业特征（岗位端特有）
    if "industry_category" in df_positions.columns:
        # 对行业类别进行Label编码
        le = LabelEncoder()
        all_industries = list(df_positions["industry_category"].dropna().unique()) + ["未知"]
        le.fit(all_industries)

        # 求职者：行业设为"未知"
        combined["industry_encoded"] = le.transform(
            combined["industry_category"].fillna("未知").apply(
                lambda x: x if x in le.classes_ else "未知"
            )
        )
        encoded_cols.append("industry_encoded")

    # 提取数值矩阵
    feature_matrix = combined[encoded_cols].values.astype(float)

    # 标准化
    scaler = MinMaxScaler()
    feature_matrix_scaled = scaler.fit_transform(feature_matrix)

    # 分离求职者和岗位向量
    seeker_mask = combined["_source"] == "seeker"
    position_mask = combined["_source"] == "position"

    seeker_vectors = feature_matrix_scaled[seeker_mask]
    position_vectors = feature_matrix_scaled[position_mask]

    print(f"  求职者向量: {seeker_vectors.shape}")
    print(f"  岗位向量: {position_vectors.shape}")
    print(f"  编码特征: {encoded_cols}")

    return seeker_vectors, position_vectors, encoded_cols, scaler, le


seeker_vecs, position_vecs, encoded_features, scaler, industry_encoder = \
    build_feature_vectors(unemployed, employed, seeker_features)

# ============================================================
# 4. 计算余弦相似度并推荐
# ============================================================
print("\n" + "=" * 60)
print("Step 4: 余弦相似度计算 & Top-K推荐")
print("=" * 60)

# 计算相似度矩阵: (n_seekers, n_positions)
similarity_matrix = cosine_similarity(seeker_vecs, position_vecs)
print(f"相似度矩阵: {similarity_matrix.shape}")
print(f"相似度范围: [{similarity_matrix.min():.4f}, {similarity_matrix.max():.4f}]")
print(f"平均相似度: {similarity_matrix.mean():.4f}")

# Top-K推荐
K = 5
top_k_indices = np.argsort(-similarity_matrix, axis=1)[:, :K]
top_k_scores = np.array([
    similarity_matrix[i, top_k_indices[i]] for i in range(len(top_k_indices))
])

print(f"为 {len(unemployed)} 名失业人员各推荐 Top-{K} 个岗位")

# ============================================================
# 5. 推荐结果整理
# ============================================================
print("\n" + "=" * 60)
print("Step 5: 推荐结果分析")
print("=" * 60)

# 岗位信息
position_info = employed[["b_aab022", "b_aab004", "industry_category"]].reset_index(drop=True)

# 为每位失业人员生成推荐
recommendations = []
for i in range(len(unemployed)):
    seeker_id = unemployed.iloc[i]["id"]
    seeker_age = unemployed.iloc[i]["age"]
    seeker_edu = unemployed.iloc[i]["edu_level"]
    seeker_sex = "男" if unemployed.iloc[i]["sex"] == 1 else "女"

    rec_jobs = []
    for k in range(K):
        job_idx = top_k_indices[i][k]
        score = top_k_scores[i][k]
        job_industry = position_info.iloc[job_idx]["industry_category"]
        job_company = position_info.iloc[job_idx]["b_aab004"]
        job_code = position_info.iloc[job_idx]["b_aab022"]

        rec_jobs.append({
            "排名": k + 1,
            "行业": job_industry if pd.notna(job_industry) else "未知",
            "行业代码": job_code if pd.notna(job_code) else "N/A",
            "单位": job_company if pd.notna(job_company) else "N/A",
            "相似度": round(score, 4),
        })

    recommendations.append({
        "求职者ID": seeker_id,
        "年龄": seeker_age,
        "学历": seeker_edu,
        "性别": seeker_sex,
        "Top1相似度": rec_jobs[0]["相似度"],
        "Top5平均相似度": round(np.mean([r["相似度"] for r in rec_jobs]), 4),
        "推荐岗位": rec_jobs,
    })

# 展示前10个求职者的推荐结果
print("\n前10位失业人员推荐结果:")
for rec in recommendations[:10]:
    print(f"\n  求职者ID={rec['求职者ID']}, 年龄={rec['年龄']}, 性别={rec['性别']}")
    for job in rec["推荐岗位"][:3]:
        print(f"    Top{job['排名']}: {job['行业']} | {job['单位'][:20] if len(str(job['单位'])) > 0 else 'N/A'} | 相似度={job['相似度']:.4f}")

# ============================================================
# 6. 统计汇总
# ============================================================
print("\n\n" + "=" * 60)
print("Step 6: 匹配统计")
print("=" * 60)

top1_scores = [r["Top1相似度"] for r in recommendations]
top5_avg_scores = [r["Top5平均相似度"] for r in recommendations]

print(f"Top-1相似度: max={max(top1_scores):.4f}, min={min(top1_scores):.4f}, "
      f"mean={np.mean(top1_scores):.4f}, median={np.median(top1_scores):.4f}")
print(f"Top-5平均相似度: max={max(top5_avg_scores):.4f}, min={min(top5_avg_scores):.4f}, "
      f"mean={np.mean(top5_avg_scores):.4f}")

# 高相似度推荐占比
high_match = sum(1 for s in top1_scores if s > 0.95)
print(f"Top1相似度>0.95: {high_match}/{len(unemployed)} ({high_match/len(unemployed)*100:.1f}%)")

# 推荐行业多样性
all_recommended_industries = []
for rec in recommendations:
    for job in rec["推荐岗位"]:
        all_recommended_industries.append(job["行业"])

from collections import Counter
industry_counter = Counter(all_recommended_industries)
print(f"\n推荐最多的行业Top10:")
for ind, count in industry_counter.most_common(10):
    print(f"  {ind}: {count} 次 ({count/len(all_recommended_industries)*100:.1f}%)")

# ============================================================
# 7. 可视化
# ============================================================
print("\n" + "=" * 60)
print("Step 7: 可视化")
print("=" * 60)

fig, axes = plt.subplots(2, 2, figsize=(14, 11))

# 7a. 相似度分布直方图
ax = axes[0, 0]
ax.hist(top1_scores, bins=40, color=COLORS[0], edgecolor="white", alpha=0.85)
ax.axvline(np.mean(top1_scores), color="red", linestyle="--", linewidth=2,
           label=f"均值={np.mean(top1_scores):.4f}")
ax.axvline(np.median(top1_scores), color="orange", linestyle="--", linewidth=2,
           label=f"中位数={np.median(top1_scores):.4f}")
ax.set_xlabel("Top-1 余弦相似度", fontsize=11)
ax.set_ylabel("求职者人数", fontsize=11)
ax.set_title("Top-1匹配相似度分布", fontsize=13, fontweight="bold")
ax.legend(fontsize=9)

# 7b. 相似度分档饼图
ax = axes[0, 1]
bins = [0, 0.5, 0.7, 0.85, 0.95, 1.01]
labels = ["<0.5", "0.5-0.7", "0.7-0.85", "0.85-0.95", "0.95-1.0"]
sim_counts = pd.cut(top1_scores, bins=bins, labels=labels).value_counts()
wedges, texts, autotexts = ax.pie(sim_counts.values, labels=sim_counts.index,
                                   autopct="%1.1f%%", colors=COLORS[:5],
                                   explode=(0, 0, 0, 0, 0.05))
ax.set_title("Top-1相似度分档占比", fontsize=13, fontweight="bold")

# 7c. 推荐行业分布Top15
ax = axes[1, 0]
top_ind = industry_counter.most_common(15)
ind_names = [x[0] for x in top_ind]
ind_counts = [x[1] for x in top_ind]
bars = ax.barh(range(len(ind_names)), ind_counts, color=COLORS[:len(ind_names)], edgecolor="white")
ax.set_yticks(range(len(ind_names)))
ax.set_yticklabels(ind_names, fontsize=9)
ax.set_xlabel("推荐次数", fontsize=11)
ax.set_title("推荐行业分布 (Top15)", fontsize=13, fontweight="bold")
ax.invert_yaxis()
for bar, val in zip(bars, ind_counts):
    ax.text(bar.get_width() + 2, bar.get_y() + bar.get_height()/2, str(val), va="center", fontsize=9)

# 7d. 匹配得分Top-N对比
ax = axes[1, 1]
position_ranks = [f"Top-{i}" for i in range(1, K+1)]
avg_scores_by_rank = [np.mean([r["推荐岗位"][i]["相似度"] for r in recommendations]) for i in range(K)]
bars = ax.bar(position_ranks, avg_scores_by_rank, color=COLORS[:K], edgecolor="white")
ax.set_ylabel("平均相似度", fontsize=11)
ax.set_title("各排名位置的平均相似度", fontsize=13, fontweight="bold")
ax.set_ylim(0, 1)
for bar, val in zip(bars, avg_scores_by_rank):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01,
            f"{val:.4f}", ha="center", fontsize=10)

plt.tight_layout()
save_chart("15_matching_analysis.png")
plt.close()

# ============================================================
# 8. 汇总输出
# ============================================================
print("\n" + "=" * 60)
print("问题四分析完成！")
print("=" * 60)
print(f"""
=== 人岗匹配模型概要 ===

[模型方法] 基于余弦相似度的多维特征匹配
[求职者数] {len(unemployed)} 人 (失业人员)
[岗位池]   {len(employed)} 个岗位 (来自就业人员)
[匹配维度] {len(encoded_features)} 个特征

[外部数据说明]
| 数据项 | 来源 | 用途 |
|--------|------|------|
| 用人单位信息 | 赛题就业数据 | 岗位画像构建 |
| 行业分类 | 赛题数据+行业代码表 | 行业匹配 |
| 岗位特征 | 就业人员信息聚合 | 岗位画像向量化 |

[匹配效果]
- 平均Top-1相似度: {np.mean(top1_scores):.4f}
- 平均Top-5相似度: {np.mean(top5_avg_scores):.4f}
- Top1相似度>0.95占比: {high_match/len(unemployed)*100:.1f}%

[推荐输出]
- 每位失业人员获得Top-5岗位推荐
- 推荐覆盖{len(industry_counter)}个行业类别
""")

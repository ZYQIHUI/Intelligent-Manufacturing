"""
就业状态分析与预测 — 数据预处理
简单Prompt版本
"""
import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings("ignore")

NULL_MARKER = "\\N"
import os
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(SCRIPT_DIR, "..", "..")  # 回到项目根目录

# ============================================================
# 1. 加载数据
# ============================================================
print("=" * 60)
print("Step 1: 加载数据")
print("=" * 60)

# 训练集 (Sheet 数据集)
df_train = pd.read_excel(
    f"{DATA_DIR}/附件1 数据.xls",
    sheet_name="数据集", header=None, skiprows=3
)
col_names = pd.read_excel(
    f"{DATA_DIR}/附件1 数据.xls",
    sheet_name="数据集", header=None, nrows=2
).iloc[1].tolist()
df_train.columns = col_names
df_train = df_train.reset_index(drop=True)
print(f"训练集: {df_train.shape[0]} 条, {df_train.shape[1]} 列")

# 预测集 (Sheet 预测集)
df_predict = pd.read_excel(
    f"{DATA_DIR}/附件1 数据.xls",
    sheet_name="预测集", header=None, skiprows=2
)
pred_cols = pd.read_excel(
    f"{DATA_DIR}/附件1 数据.xls",
    sheet_name="预测集", header=None, nrows=1
).iloc[0].tolist()
pred_cols = [str(c) for c in pred_cols]
df_predict.columns = pred_cols
df_predict = df_predict.reset_index(drop=True)
# 重命名预测集的people_id为id以对齐(或者保持独立)
# 预测集有"预测"列作为ground truth
print(f"预测集: {df_predict.shape[0]} 条, {df_predict.shape[1]} 列")
print(f"预测集列名: {df_predict.columns.tolist()}")

# 字段注释
df_annotations = pd.read_excel(
    f"{DATA_DIR}/附件1 数据.xls",
    sheet_name="字段注释", header=None, skiprows=1
)
df_annotations.columns = ["字段", "注释", "备注"]
print(f"\n字段注释: {len(df_annotations)} 条")

# 行业代码
df_industry = pd.read_excel(
    f"{DATA_DIR}/附件1 数据.xls",
    sheet_name="行业代码", header=None, skiprows=1
)
df_industry.columns = ["行业代码", "行业名称"]
print(f"行业代码对照: {len(df_industry)} 条")

# ============================================================
# 2. 统一NULL标记
# ============================================================
print("\n" + "=" * 60)
print("Step 2: 统一NULL标记")
print("=" * 60)


def clean_null(df):
    """将\\N统一替换为NaN"""
    for col in df.columns:
        df[col] = df[col].apply(
            lambda x: np.nan if (pd.notna(x) and str(x).strip() == NULL_MARKER) else x
        )
    return df


df_train = clean_null(df_train)
df_predict = clean_null(df_predict)

print(f"训练集总缺失数: {df_train.isna().sum().sum()}")
print(f"预测集总缺失数: {df_predict.isna().sum().sum()}")

# ============================================================
# 3. 构建就业状态标签
# ============================================================
print("\n" + "=" * 60)
print("Step 3: 构建就业状态标签")
print("=" * 60)

# 关键字段:
#   b_acc031: 就业时间
#   c_ajc090: 失业时间
#   b_acc033: 是否签订劳动合同 (1=是)
#   b_aab004: 录用单位
#   c_acc028: 失业注销时间 (有值说明已注销失业登记→已就业)

# 将时间字段转为datetime
for col in ["b_acc031", "c_ajc090", "c_acc028"]:
    if col in df_train.columns:
        df_train[col] = pd.to_datetime(df_train[col], errors="coerce")


def build_employment_label(row):
    """
    构建就业状态标签: 1=就业, 0=失业
    规则(参考范例报告):
    1. 仅有就业时间无失业时间 → 就业(1)
    2. 仅有无业时间无就业时间 → 失业(0)
    3. 两者都有 → 比较时间: 就业时间晚于失业时间 → 就业(1), 否则失业(0)
    4. 两者都无 → 检查劳动合同/录用单位
    """
    has_employ = pd.notna(row["b_acc031"])
    has_unemploy = pd.notna(row["c_ajc090"])
    has_contract = pd.notna(row["b_acc033"]) and str(row["b_acc033"]).strip() == "1"
    has_company = pd.notna(row["b_aab004"]) and str(row["b_aab004"]).strip() != ""
    has_unemploy_cancel = pd.notna(row["c_acc028"])  # 失业注销时间

    if has_employ and not has_unemploy:
        return 1
    elif has_unemploy and not has_employ:
        return 0
    elif has_employ and has_unemploy:
        # 比较时间先后
        if row["b_acc031"] > row["c_ajc090"]:
            return 1
        else:
            return 0
    elif has_unemploy_cancel:
        # 失业已注销 → 就业
        return 1
    elif has_contract or has_company:
        return 1
    else:
        return 0


df_train["employment_status"] = df_train.apply(build_employment_label, axis=1)

emp_count = (df_train["employment_status"] == 1).sum()
unemp_count = (df_train["employment_status"] == 0).sum()
print(f"就业: {emp_count} 人 ({emp_count / len(df_train) * 100:.1f}%)")
print(f"失业: {unemp_count} 人 ({unemp_count / len(df_train) * 100:.1f}%)")

# ============================================================
# 4. 数据类型转换与编码
# ============================================================
print("\n" + "=" * 60)
print("Step 4: 特征编码")
print("=" * 60)

# 数值型列
numeric_cols = ["age"]
for col in numeric_cols:
    if col in df_train.columns:
        df_train[col] = pd.to_numeric(df_train[col], errors="coerce")

# 分类列编码
categorical_cols = [
    "sex", "nation", "marriage", "edu_level", "politic",
    "religion", "c_aac009", "c_aac011", "type",
    "military_status", "is_disability", "is_teen", "is_elder",
    "change_type", "is_living_alone", "live_status",
    "b_acc033", "b_acc034", "c_ajc093", "c_acc023", "acc02y"
]

for col in categorical_cols:
    if col in df_train.columns:
        df_train[col] = pd.to_numeric(df_train[col], errors="coerce")

# 行业代码首字母归类
df_train["industry_category"] = df_train["b_aab022"].apply(
    lambda x: str(x)[0] if pd.notna(x) and len(str(x)) > 0 else np.nan
)

# 学历映射
edu_map = {10: "初中及以下", 20: "中专/高中", 30: "专科/本科及以上"}
df_train["edu_label"] = df_train["edu_level"].map(edu_map)

# 性别映射
sex_map = {1: "男", 2: "女"}
df_train["sex_label"] = df_train["sex"].map(sex_map)

# 婚姻状态映射
marriage_map = {10: "未婚", 20: "已婚", 30: "离婚", 40: "丧偶"}
df_train["marriage_label"] = df_train["marriage"].map(marriage_map)

# 户口性质
hukou_map = {"10": "农业", "11": "农业", "12": "农业",
             "20": "非农业", "21": "非农业", "22": "非农业", "50": "统一居民户口"}
df_train["hukou_label"] = df_train["c_aac009"].astype(str).map(hukou_map)

# 年龄分段
bins = [0, 25, 35, 45, 55, 100]
labels = ["16-25岁", "26-35岁", "36-45岁", "46-55岁", "56岁以上"]
df_train["age_group"] = pd.cut(
    df_train["age"], bins=bins, labels=labels, right=True
)

print("特征编码完成")
print(f"行业大类: {df_train['industry_category'].value_counts().to_dict()}")

# ============================================================
# 5. 缺失值处理
# ============================================================
print("\n" + "=" * 60)
print("Step 5: 缺失值处理")
print("=" * 60)

# 对于建模用的特征:
# - 极高缺失率(>80%)的列直接丢弃
# - 分类变量: 填充为"未知"类别
# - 数值变量: 中位数填充

high_missing_cols = [
    "note", "c_aca112", "c_acc027", "c_aca111", "acc02y",
    "c_acc026", "b_acc034", "c_acc0m3", "c_acc023", "live_status"
]
print(f"丢弃高缺失率列({len(high_missing_cols)}列): {high_missing_cols}")

# 对保留的分类特征填充
model_categorical_cols = [
    "sex", "nation", "marriage", "edu_level", "politic",
    "religion", "c_aac009", "c_aac011", "type",
    "military_status", "is_disability", "is_teen", "is_elder",
    "change_type", "is_living_alone"
]
for col in model_categorical_cols:
    if col in df_train.columns:
        # 用众数填充
        mode_val = df_train[col].mode()
        if len(mode_val) > 0:
            df_train[col] = df_train[col].fillna(mode_val[0])

# profession字段特殊处理 - 缺失较多但可能有信息价值
df_train["profession_has_value"] = df_train["profession"].notna().astype(int)

print("缺失值处理完成")

# ============================================================
# 6. 保存预处理结果
# ============================================================
print("\n" + "=" * 60)
print("Step 6: 保存预处理结果")
print("=" * 60)

# 保存完整训练集
df_train.to_csv(os.path.join(SCRIPT_DIR, "train_clean.csv"), index=False, encoding="utf-8-sig")
df_predict.to_csv(os.path.join(SCRIPT_DIR, "predict_clean.csv"), index=False, encoding="utf-8-sig")

# 保存关键统计信息 (供后续报告使用)
stats = {
    "total_samples": len(df_train),
    "employed": int(emp_count),
    "unemployed": int(unemp_count),
    "employment_rate": round(emp_count / len(df_train) * 100, 2),
    "age_mean": round(df_train["age"].mean(), 1),
    "age_median": round(df_train["age"].median(), 1),
    "age_min": int(df_train["age"].min()),
    "age_max": int(df_train["age"].max()),
    "male_count": int((df_train["sex"] == 1).sum()),
    "female_count": int((df_train["sex"] == 2).sum()),
}
print(f"统计摘要: {stats}")

# 输出标签分布表 (示例表1)
print("\n" + "=" * 60)
print("示例表1: 当前就业状态")
print("=" * 60)
print(f"{'就业失业状态':<15} {'就业':<10} {'失业':<10}")
print(f"{'数量（人）':<15} {emp_count:<10} {unemp_count:<10}")

print("\n预处理完成! 文件已保存到 prompt版本/数据预处理/ 目录")

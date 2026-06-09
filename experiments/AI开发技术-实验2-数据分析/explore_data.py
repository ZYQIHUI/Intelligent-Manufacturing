import pandas as pd
import numpy as np

df = pd.read_excel("附件1 数据.xls", header=None, skiprows=3)
col_names = pd.read_excel("附件1 数据.xls", header=None, nrows=2).iloc[1].tolist()
df.columns = col_names
df = df.reset_index(drop=True)

NULL_MARKER = "\\N"
employ_cols = col_names[30:39]
unemploy_cols = col_names[39:54]

def has_info(val):
    if pd.isna(val):
        return False
    s = str(val).strip()
    return s != NULL_MARKER and s != ""

# ============================================================
# 1. c_acc0m3 - 登记就失业状态
# ============================================================
print("=" * 60)
print("1. c_acc0m3 (登记就失业状态)")
print("=" * 60)
print(df["c_acc0m3"].value_counts(dropna=False))
print()

# ============================================================
# 2. \\N 值分布
# ============================================================
print("=" * 60)
print("2. \\N 值分布 (NULL标记)")
print("=" * 60)
for col in df.columns:
    count = (df[col] == NULL_MARKER).sum()
    if count > 0:
        pct = count / len(df) * 100
        print(f"  {col}: {count} ({pct:.1f}%)")

print()

# ============================================================
# 3. 查找预测集 (20个仅有个人信息的样本)
# ============================================================
print("=" * 60)
print("3. 查找预测集")
print("=" * 60)

df["emp_info_count"] = df[employ_cols].apply(
    lambda row: sum(has_info(v) for v in row), axis=1
)
df["unemp_info_count"] = df[unemploy_cols].apply(
    lambda row: sum(has_info(v) for v in row), axis=1
)
df["total_info_count"] = df["emp_info_count"] + df["unemp_info_count"]

no_info = df[df["total_info_count"] == 0]
print(f"完全无就业/失业信息的样本: {len(no_info)}")
if len(no_info) > 0:
    print(f"  行索引: {no_info.index.tolist()}")
    print(f"  id: {no_info['id'].tolist()}")

# 查看acc02y字段
print(f"\nacc02y 取值: {df['acc02y'].value_counts(dropna=False).to_dict()}")

# 查看尾部
print(f"\n尾部3行 total_info_count:")
print(df[["id", "emp_info_count", "unemp_info_count", "total_info_count"]].tail(5))

print()

# ============================================================
# 4. 关键时间字段
# ============================================================
print("=" * 60)
print("4. 关键时间字段")
print("=" * 60)
for col in ["birthday", "b_acc031", "c_ajc090", "c_acc02e",
            "c_acc03b", "c_acc028", "b_aae030", "b_aae031"]:
    if col in df.columns:
        valid_mask = df[col].apply(has_info)
        print(f"  {col}: {valid_mask.sum()}条有效记录")
        if valid_mask.sum() > 0:
            samples = df.loc[valid_mask, col].head(3).tolist()
            print(f"    样例: {samples}")

print()

# ============================================================
# 5. 基础统计信息
# ============================================================
print("=" * 60)
print("5. 训练集基础统计")
print("=" * 60)
train = df[df["total_info_count"] > 0].copy()
print(f"训练集样本数: {len(train)}")

# 年龄分布
ages = pd.to_numeric(train["age"], errors="coerce")
print(f"\n年龄: min={ages.min():.0f}, max={ages.max():.0f}, "
      f"mean={ages.mean():.1f}, median={ages.median():.0f}")

# 按年龄段
bins = [0, 25, 35, 45, 55, 100]
labels = ["16-25", "26-35", "36-45", "46-55", "56+"]
train["age_group"] = pd.cut(ages, bins=bins, labels=labels, right=True)
print(f"\n年龄段分布:")
print(train["age_group"].value_counts().sort_index())

# 性别
print(f"\n性别: 1=男, 2=女")
print(train["sex"].value_counts())

# 教育程度
print(f"\n教育程度: 10=初中及以下, 20=中专/高中, 30=专科/本科")
print(train["edu_level"].value_counts().sort_index())

# 民族
print(f"\n民族 (1=汉族):")
print(train["nation"].value_counts().head(10))

# ============================================================
# 6. 缺失值总览 (训练集)
# ============================================================
print("\n" + "=" * 60)
print("6. 训练集缺失值统计 (含\\N)")
print("=" * 60)

def is_missing(val):
    if pd.isna(val):
        return True
    return str(val).strip() == NULL_MARKER

missing_stats = []
for col in df.columns:
    miss_count = train[col].apply(is_missing).sum()
    if miss_count > 0:
        missing_stats.append({
            "列名": col,
            "缺失数": miss_count,
            "缺失率%": round(miss_count / len(train) * 100, 2)
        })

missing_df = pd.DataFrame(missing_stats).sort_values("缺失数", ascending=False)
print(missing_df.to_string(index=False))

"""
就业状态分析与预测 — 数据预处理 (Skill增强版)
应用 data-analyst-prompter 方法论: EDA优先 + 假设验证 + 代码执行
"""
import pandas as pd
import numpy as np
import os
import warnings
warnings.filterwarnings("ignore")

# ============================================================
# Phase 0: Schema注入 & 元数据准备
# ============================================================
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(SCRIPT_DIR, "..", "..")
DATA_FILE = os.path.join(DATA_DIR, "附件1 数据.xls")

NULL_MARKER = "\\N"
RANDOM_STATE = 42

# Schema定义 (来自字段注释Sheet)
SCHEMA = {
    "个人基本信息(Col0-29)": {
        "id": "记录序号",
        "people_id": "人员编号",
        "name": "姓名(脱敏)",
        "sex": "性别 (1=男, 2=女)",
        "birthday": "出生日期",
        "age": "年龄",
        "nation": "民族代码 (1=汉族, 15=土家族等)",
        "marriage": "婚姻状态 (10=未婚, 20=已婚, 30=离婚, 40=丧偶)",
        "edu_level": "教育程度 (10=初中及以下, 20=中专/高中, 30=专科/本科及以上)",
        "politic": "政治面貌",
        "reg_address": "户籍地址",
        "profession": "专业代码",
        "religion": "宗教信仰",
        "c_aac009": "户口性质",
        "c_aab299": "户口所在地区(代码)",
        "c_aac010": "户口所在地区(名称)",
        "c_aac011": "文化程度代码",
        "c_aac180": "毕业学校",
        "c_aac181": "毕业日期",
        "c_aac182": "所学专业代码",
        "c_aac183": "所学专业名称",
        "type": "人口类型",
        "military_status": "兵役状态",
        "is_disability": "是否残疾人",
        "is_teen": "是否青少年",
        "is_elder": "是否老年人",
        "change_type": "变动类型",
        "is_living_alone": "是否独居",
        "live_status": "居住状态",
        "note": "备注",
    },
    "就业信息(Col30-38)": {
        "b_acc030": "就业登记编号",
        "b_aab001": "录用单位编号",
        "b_acc031": "就业时间",
        "b_acc033": "是否签订劳动合同",
        "b_acc034": "是否参加社会保险",
        "b_aae030": "合同起始日期",
        "b_aae031": "合同终止日期",
        "b_aab022": "行业代码",
        "b_aab004": "录用单位名称",
    },
    "失业信息(Col39-53)": {
        "c_acc02e": "失业审核日期",
        "c_acc020": "失业登记编号",
        "c_ajc090": "失业时间",
        "c_ajc093": "失业原因",
        "c_aca111": "原从事工种代码",
        "c_aca112": "原从事工种名称",
        "c_aac013": "原用工形式",
        "c_acc026": "求职意愿",
        "c_acc027": "培训意愿",
        "c_acc03b": "失业信息登记表登记日期",
        "c_acc028": "失业注销时间",
        "c_acc0m3": "登记就失业状态",
        "c_acc023": "失业类型",
        "c_aab004": "原单位名称",
        "acc02y": "是否享受失业保险待遇",
    },
}

# ============================================================
# Phase 1: EDA - 探索性数据分析
# ============================================================
print("=" * 60)
print("PHASE 1: EDA - 探索性数据分析")
print("=" * 60)

# 加载数据
xls = pd.ExcelFile(DATA_FILE)
print(f"\n[Schema] Excel包含 {len(xls.sheet_names)} 个Sheet: {xls.sheet_names}")

# 训练集 (单次读取，避免重复读Sheet)
raw_train = pd.read_excel(DATA_FILE, sheet_name="数据集", header=None)
col_names = raw_train.iloc[1].tolist()
df_train = raw_train.iloc[3:].reset_index(drop=True)
df_train.columns = col_names
print(f"\n[数据集] Shape: {df_train.shape}")

# 预测集 (单次读取，避免重复读Sheet)
raw_predict = pd.read_excel(DATA_FILE, sheet_name="预测集", header=None)
pred_cols = raw_predict.iloc[0].tolist()
pred_cols = [str(c) for c in pred_cols]
df_predict = raw_predict.iloc[2:].reset_index(drop=True)
df_predict.columns = pred_cols
print(f"[预测集] Shape: {df_predict.shape}")

# === EDA Check 1: 数据类型 ===
print("\n--- EDA Check 1: 数据类型 ---")
dtype_counts = df_train.dtypes.value_counts()
print(dtype_counts)

# === EDA Check 2: \N空值标记 ===
print("\n--- EDA Check 2: \\\\N空值标记分布 ---")
slash_n_series = (df_train == NULL_MARKER).sum()
slash_n_cols = slash_n_series[slash_n_series > 0].to_dict()

# 按缺失率分层
print(f"存在\\\\N的列数: {len(slash_n_cols)}")
print(f"\n极端缺失(>95%): {sum(1 for v in slash_n_cols.values() if v/len(df_train) > 0.95)}列")
for col, cnt in sorted(slash_n_cols.items(), key=lambda x: x[1], reverse=True):
    pct = cnt / len(df_train) * 100
    if pct > 50:
        print(f"  {col}: {cnt} ({pct:.1f}%)")

print(f"\n中度缺失(10%-50%): {sum(1 for v in slash_n_cols.values() if 0.1 <= v/len(df_train) <= 0.5)}列")
print(f"低度缺失(<10%): {sum(1 for v in slash_n_cols.values() if v/len(df_train) < 0.1)}列")

# === EDA Check 3: 基本统计 ===
print("\n--- EDA Check 3: 基本统计量 ---")
ages = pd.to_numeric(df_train["age"], errors="coerce")
print(f"年龄: min={ages.min():.0f}, max={ages.max():.0f}, "
      f"mean={ages.mean():.1f}, median={ages.median():.0f}, std={ages.std():.1f}")

# === EDA Check 4: 关键字段取值 ===
print("\n--- EDA Check 4: 关键字段分布 ---")
print(f"性别: {(df_train['sex']==1).sum()}男 / {(df_train['sex']==2).sum()}女")
print(f"教育程度: {df_train['edu_level'].value_counts().sort_index().to_dict()}")
print(f"婚姻状态: {df_train['marriage'].value_counts().sort_index().to_dict()}")

# === EDA Check 5: 预测集特征确认 ===
print("\n--- EDA Check 5: 预测集验证 ---")
predict_only_cols = set(df_predict.columns) - {"预测"}
train_cols = set(df_train.columns)
common = predict_only_cols & train_cols
missing_in_predict = predict_only_cols - train_cols
print(f"预测集与训练集共有特征: {len(common)}个")
if missing_in_predict:
    print(f"预测集独有(训练集缺失): {missing_in_predict}")

# ============================================================
# Phase 2: 数据清洗 (Data Cleaning Protocol)
# ============================================================
print("\n" + "=" * 60)
print("PHASE 2: 数据清洗")
print("=" * 60)


def clean_null(df):
    """Rule 1: \\N -> NaN (统一空值标记) — 向量化替换"""
    return df.replace({NULL_MARKER: np.nan})


df_train = clean_null(df_train)
df_predict = clean_null(df_predict)

# 统计清洗后缺失情况
total_missing = df_train.isna().sum().sum()
print(f"清洗后训练集总缺失数: {total_missing}")
print(f"清洗后预测集总缺失数: {df_predict.isna().sum().sum()}")

# ============================================================
# Phase 3: 假设-验证 — 就业状态标签构建
# ============================================================
print("\n" + "=" * 60)
print("PHASE 3: 就业状态标签构建 (假设-验证框架)")
print("=" * 60)

# H1: 同时有就业和失业时间的人，较晚的时间决定当前状态
# H2: 仅有就业信息 → 就业
# H3: 仅有失业信息 → 失业
# H4: 两者都无但有劳动合同/单位 → 就业
# H5: 有失业注销时间 → 已重新就业

for col in ["b_acc031", "c_ajc090", "c_acc028", "b_aae030", "b_aae031"]:
    if col in df_train.columns:
        df_train[col] = pd.to_datetime(df_train[col], errors="coerce")

# 向量化标签构建 (替代逐行apply)
has_emp = df_train["b_acc031"].notna()
has_unemp = df_train["c_ajc090"].notna()
has_cancel = df_train.get("c_acc028").notna() if "c_acc028" in df_train.columns else pd.Series(False, index=df_train.index)

b_acc033 = df_train.get("b_acc033", pd.Series(index=df_train.index))
has_contract = b_acc033.notna() & b_acc033.astype(str).str.strip().eq("1")

b_aab004 = df_train.get("b_aab004", pd.Series(index=df_train.index))
has_company = b_aab004.notna() & b_aab004.astype(str).str.strip().ne("")

conditions = [
    has_emp & ~has_unemp,
    has_unemp & ~has_emp,
    has_cancel,
    has_contract | has_company,
]
choices = [1, 0, 1, 1]
df_train["employment_status"] = np.select(conditions, choices, default=0)

# 处理两者都有的情况: 较晚的时间决定状态
mask_both = has_emp & has_unemp
if mask_both.any():
    df_train.loc[mask_both, "employment_status"] = (
        df_train.loc[mask_both, "b_acc031"] > df_train.loc[mask_both, "c_ajc090"]
    ).astype(int)

emp_cnt = (df_train["employment_status"] == 1).sum()
unemp_cnt = (df_train["employment_status"] == 0).sum()
emp_rate = emp_cnt / len(df_train) * 100
print(f"\n[验证结果]")
print(f"  就业: {emp_cnt}人 ({emp_rate:.1f}%)")
print(f"  失业: {unemp_cnt}人 ({100-emp_rate:.1f}%)")
print(f"  就失业比: {emp_cnt/unemp_cnt:.2f}:1 → 存在类别不平衡，后续建模需处理")

# ============================================================
# Phase 4: 特征工程 (Feature Engineering)
# ============================================================
print("\n" + "=" * 60)
print("PHASE 4: 特征工程")
print("=" * 60)

# 4a. 类型转换
for col in ["age"]:
    df_train[col] = pd.to_numeric(df_train[col], errors="coerce")

cat_cols = [
    "sex", "nation", "marriage", "edu_level", "politic", "religion",
    "c_aac009", "c_aac011", "type", "military_status", "is_disability",
    "is_teen", "is_elder", "change_type", "is_living_alone",
]
for col in cat_cols:
    if col in df_train.columns:
        df_train[col] = pd.to_numeric(df_train[col], errors="coerce")
    if col in df_predict.columns:
        df_predict[col] = pd.to_numeric(df_predict[col], errors="coerce")

# 4b. 行业大类 (向量化str方法替代逐行apply)
col_str = df_train["b_aab022"].astype(str).str.strip()
df_train["industry_category"] = col_str.str[0].where(
    df_train["b_aab022"].notna() & col_str.str.len().gt(0), np.nan
)

# 4c. 标签映射
df_train["edu_label"] = df_train["edu_level"].map(
    {10: "初中及以下", 20: "中专/高中", 30: "专科/本科及以上"}
)
df_train["sex_label"] = df_train["sex"].map({1: "男", 2: "女"})
df_train["marriage_label"] = df_train["marriage"].map(
    {10: "未婚", 20: "已婚", 30: "离婚", 40: "丧偶"}
)
df_train["hukou_label"] = df_train["c_aac009"].map({
    10: "农业", 11: "农业", 12: "农业",
    20: "非农业", 21: "非农业", 22: "非农业",
    50: "统一居民户口",
})

# 4d. 年龄分段
df_train["age_group"] = pd.cut(
    df_train["age"], bins=[0, 25, 35, 45, 55, 100],
    labels=["16-25岁", "26-35岁", "36-45岁", "46-55岁", "56岁以上"], right=True
)

# 4e. profession特征(处理23%缺失)
df_train["profession_has_value"] = df_train["profession"].notna().astype(int)

print("特征工程完成: 新增 edu_label/sex_label/marriage_label/hukou_label/age_group/industry_category/profession_has_value")

# ============================================================
# Phase 5: 缺失值处理策略
# ============================================================
print("\n" + "=" * 60)
print("PHASE 5: 缺失值处理")
print("=" * 60)

# 计算缺失率
missing_pct = df_train.isna().sum() / len(df_train)

# 极端缺失(>80%): 丢弃
drop_cols = missing_pct[missing_pct > 0.80].index.tolist()
print(f"丢弃列 (缺失率>80%, {len(drop_cols)}列): {drop_cols}")

# 保留列的缺失值填充 (使用Skill增强策略: 众数填充而非简单中位数)
keep_cat_cols = [c for c in cat_cols if c not in drop_cols and c in df_train.columns]
for col in keep_cat_cols:
    if df_train[col].isna().any():
        mode_val = df_train[col].mode()
        fill_val = mode_val[0] if len(mode_val) > 0 else 0
        df_train[col] = df_train[col].fillna(fill_val)

# 预测集同样处理
for col in keep_cat_cols:
    if col in df_predict.columns and df_predict[col].isna().any():
        mode_val = df_train[col].mode()
        fill_val = mode_val[0] if len(mode_val) > 0 else 0
        df_predict[col] = df_predict[col].fillna(fill_val)

print(f"分类特征填充完成: {len(keep_cat_cols)}个特征")

# ============================================================
# Phase 6: 保存
# ============================================================
print("\n" + "=" * 60)
print("PHASE 6: 保存预处理结果")
print("=" * 60)

train_path = os.path.join(SCRIPT_DIR, "train_clean.csv")
predict_path = os.path.join(SCRIPT_DIR, "predict_clean.csv")
df_train.to_csv(train_path, index=False, encoding="utf-8-sig")
df_predict.to_csv(predict_path, index=False, encoding="utf-8-sig")

print(f"训练集: {train_path} ({len(df_train)}行 × {len(df_train.columns)}列)")
print(f"预测集: {predict_path} ({len(df_predict)}行 × {len(df_predict.columns)}列)")

# 验证保存 (直接检查内存DataFrame，避免无效CSV重读)
assert len(df_train) > 0, "训练集为空!"
assert "employment_status" in df_train.columns, "标签列缺失!"
print("\n数据验证通过 ✓")

print("\n" + "=" * 60)
print("数据预处理完成 (Skill增强版)")
print(f"处理策略: EDA优先 → \\\\N清洗 → 标签构建(5假设验证) → 特征工程 → 缺失值众数填充")
print("=" * 60)

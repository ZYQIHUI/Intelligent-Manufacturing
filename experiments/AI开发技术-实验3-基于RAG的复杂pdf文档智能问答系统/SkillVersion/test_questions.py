#!/usr/bin/env python
"""
4道样本测试题 —— 验证 RAG 问答系统 (SkillVersion)
使用社区 rag-implementation + frontend-design + 自定义 pdf-parser 技能
"""
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env")

from config import Config
from embedding_engine import EmbeddingEngine
from vector_store import MilvusStore
from openai import OpenAI

print("=" * 60)
print("  SkillVersion — 问答测试 (社区 Skill + 自定义 Skill)")
print("=" * 60)

print("\n加载 Embedding 模型...")
embed = EmbeddingEngine()
print(f"向量维度: {embed.dim}\n")

store = MilvusStore()
store.ensure_loaded()
print(f"数据库统计: {store.get_stats()}\n")

llm = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url=os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com"),
)
model = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")


def search_all(query, top_k=8):
    query_emb = embed.embed_query(query)
    text_results = store.search("text", query_emb, top_k=top_k)
    image_results = store.search("image", query_emb, top_k=max(2, top_k // 2))

    seen = set()
    merged = []
    for r in text_results:
        key = r["text"][:100]
        if key not in seen:
            seen.add(key)
            merged.append(r)
    for r in image_results:
        key = r["text"][:100]
        if key not in seen:
            seen.add(key)
            merged.append(r)
    return merged


questions = [
    "截至2023年7月7日，从宽基指数来看，创业板指处于估值分位数的什么等级？",
    "沪深300上涨家数占比情绪指标的计算方法是什么？",
    "从宽基指数表现上看，沪深300的开盘价是多少？",
    "在中信一级行业指数估值中，有色金属的PE（TTM）值是多少？",
]

expected = [
    "安全",
    "沪深300指数N日上涨家数占比=沪深300指数成分股过去N日收益大于0的个股数占比",
    "3853.29",
    "14.84",
]

SEP = "=" * 60

for idx, q in enumerate(questions, 1):
    print(SEP)
    print(f"[Question {idx}] {q}")
    print(SEP)

    ctx = search_all(q)

    print("\n--- Retrieved Context ---")
    for i, c in enumerate(ctx):
        print(f"  [{i+1}] type={c['type']} page={c['page']} score={c['score']:.4f}")
        snippet = c["text"][:200].replace("\n", "\\n")
        print(f"      text={snippet}...")
    print()

    ctx_str = "\n\n---\n\n".join(
        [
            f"[source {i + 1}] type: {c['type']} | page: {c['page']}\n{c['text']}"
            for i, c in enumerate(ctx)
        ]
    )

    prompt = f"""你是一个专业的金融研报分析助手。请根据以下从PDF文档中检索到的信息，准确回答用户的问题。

## 规则
- 如果检索信息足以回答问题，请给出准确、详细的答案。
- 如果涉及数据，必须给出具体数值。
- 如果检索信息不足以回答问题，请明确说明原因。
- 用中文回答。

## 检索信息
{ctx_str}

## 用户问题
{q}

## 回答"""

    resp = llm.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=512,
        temperature=0.1,
    )
    answer = resp.choices[0].message.content
    print("--- Answer ---")
    print(answer)
    print()
    print("--- Expected Key Info ---")
    print(f"  Should contain: {expected[idx-1]}")
    print()

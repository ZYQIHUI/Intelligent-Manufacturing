#!/usr/bin/env python
"""Test script for the 4 sample questions"""
import os, sys, json
from pathlib import Path
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env")

from pymilvus import MilvusClient
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from openai import OpenAI

print("Loading embedding model...")
embed = HuggingFaceEmbedding(
    model_name="BAAI/bge-small-zh-v1.5", max_length=512, trust_remote_code=True
)
print("Embedding model loaded")

client = MilvusClient(str(PROJECT_ROOT / "data" / "milvus.db"))
for col in ["text_collection", "image_collection"]:
    client.load_collection(col)
print("Collections loaded\n")

llm = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url=os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com"),
)
model = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")


def search_col(col_name, q_emb, limit):
    if not client.has_collection(col_name):
        return []
    r = client.search(col_name, [q_emb], limit=limit, output_fields=["text", "page", "type"])
    if not r or not r[0]:
        return []
    hits = []
    for item in r[0]:
        e = item.get("entity", {})
        hits.append({
            "score": item.get("distance", 0),
            "text": e.get("text", ""),
            "page": e.get("page", 0),
            "type": e.get("type", ""),
        })
    return hits


def search_all(q, top_k=8):
    q_emb = embed.get_text_embedding(q)
    text_results = search_col("text_collection", q_emb, limit=top_k)
    image_results = search_col("image_collection", q_emb, limit=max(2, top_k // 2))

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
        snippet = c['text'][:200].replace('\n', '\\n')
        print(f"      text={snippet}...")
    print()

    ctx_str = "\n\n---\n\n".join(
        [
            f"[source {i+1}] type: {c['type']} | page: {c['page']}\n{c['text']}"
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
    print(f"--- Answer ---")
    print(answer)
    print()
    print(f"--- Expected Key Info ---")
    print(f"  Should contain: {expected[idx-1]}")
    print()

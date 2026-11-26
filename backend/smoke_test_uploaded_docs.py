import time
from app.knowledge.rag_engine import rag_engine
from app.knowledge.retrieval import hybrid_search

q = (
    "How do post-milking teat dipping and cow-side subclinical mastitis testing "
    "(such as the California Mastitis Test) affect subclinical mastitis prevalence in "
    "lactating dairy cows, and what body condition score (BCS) targets and management "
    "stages are recommended for dairy cows and heifers in BCS score.pdf?"
)

hits = hybrid_search(q, top_k=6, verbose=False)
print("=== TOP HYBRID HITS ===")
for i, h in enumerate(hits, 1):
    meta = h.get("metadata") or {}
    src = meta.get("filename") or meta.get("source") or "unknown"
    pg = meta.get("page") or meta.get("page_number")
    print(f"Hit {i}: rerank={h.get('rerank_score')} | src={src} | page={pg} | text={(h.get('text') or '')[:85]!r}")

t0 = time.perf_counter()
res = rag_engine.search(q)
dt = (time.perf_counter() - t0) * 1000

print("\n=== RAG ENGINE SEARCH RESULT ===")
print(f"grounded={res['grounded']} | used_db={'farm_db_data' in res} | time={dt:.0f} ms")
print("sources:", res["sources"])
print("topic:", res["topic"])
print("clinical_answer:", res["clinical_answer"])
print("spoken_response:", res["spoken_response"])

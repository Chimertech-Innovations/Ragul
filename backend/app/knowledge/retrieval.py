import json
import re
import chromadb

from pathlib import Path
from sentence_transformers import SentenceTransformer, CrossEncoder
from rank_bm25 import BM25Okapi


# ==========================================
# 1. CONFIGURATION
# ==========================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DB_PATH = PROJECT_ROOT / "data" / "vector_db"
COLLECTION_NAME = "cattle_knowledge"

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
RERANKER_NAME = "cross-encoder/ms-marco-MiniLM-L-6-v2"

CHUNKS_FILE = PROJECT_ROOT / "data" / "chunks.jsonl"

RRF_K = 60
CANDIDATE_K = 20

DOMAIN_EXPANSIONS = {
    r"\bbcs\b": [
        "body condition score",
        "body condition scoring",
        "body condition assessment",
        "condition score in dairy cattle",
        "cow body condition",
        "body reserves",
        "fat cover",
        "tailhead",
        "loin",
        "BCS scale",
    ],
    r"\bmooposhaq\b": [
        "supplementary feed",
        "energy protein supplement",
        "low body condition ration",
        "cattle nutrition recovery",
    ],
    r"\bmastitis\b": [
        "udder inflammation",
        "somatic cell count",
        "CMT",
        "California Mastitis Test",
        "quadmastest",
        "teat canal infection",
    ],
    r"\b(estrus|heat)\b": [
        "standing heat",
        "mounting behavior",
        "artificial insemination window",
        "reproductive cycle",
    ],
    r"\b(dairynz|compliance|welfare)\b": [
        "animal welfare code",
        "body condition standard",
        "milking cow welfare",
        "remedial feeding",
    ],
}


# ==========================================
# 2. LOAD EMBEDDING MODEL
# ==========================================

print("Loading embedding model...", flush=True)

model = SentenceTransformer(MODEL_NAME)


# ==========================================
# 3. LOAD RERANKING MODEL
# ==========================================

print("Loading cross-encoder reranking model...", flush=True)

reranker = CrossEncoder(RERANKER_NAME)

print("Reranking model loaded!", flush=True)


# ==========================================
# 4. CONNECT TO CHROMADB
# ==========================================

print(f"Connecting to ChromaDB at: {DB_PATH}", flush=True)

if not DB_PATH.exists():
    raise FileNotFoundError(
        f"ChromaDB directory not found: {DB_PATH}"
    )

client = chromadb.PersistentClient(
    path=str(DB_PATH)
)

collection = client.get_or_create_collection(
    name=COLLECTION_NAME
)

print(
    f"ChromaDB connected! "
    f"Collection contains {collection.count()} chunks.",
    flush=True
)


# ==========================================
# 5. LOAD DOCUMENT CHUNKS
# ==========================================

print(f"Loading document chunks from: {CHUNKS_FILE}", flush=True)

if not CHUNKS_FILE.exists():
    raise FileNotFoundError(
        f"chunks.jsonl not found: {CHUNKS_FILE}"
    )

chunks = []

with open(CHUNKS_FILE, "r", encoding="utf-8") as file:
    for line in file:
        if line.strip():
            chunks.append(json.loads(line))

if not chunks:
    raise ValueError("No document chunks found!")

print(f"Loaded {len(chunks)} chunks!", flush=True)


# ==========================================
# 6. TOKENIZATION WITH STOPWORD REMOVAL
# ==========================================

STOP_WORDS = {
    "what", "is", "the", "a", "an",
    "in", "on", "at", "of", "for",
    "to", "and", "or", "are", "was",
    "were", "be", "been", "being",
    "does", "do", "did", "how",
    "why", "when", "where", "which",
    "with", "from", "by", "about",
    "can", "could", "would", "should",
    "this", "that", "these", "those",
    "it", "its", "their", "they",
    "he", "she", "we", "you", "i"
}


def tokenize(text):
    words = re.findall(r"\b\w+\b", (text or "").lower())
    return [
        word for word in words
        if word not in STOP_WORDS
    ]


# ==========================================
# 7. QUERY EXPANSION
# ==========================================

def expand_query(question, verbose=False):
    """
    Expand recognised cattle-health, nutrition, and compliance terms
    into related terminology for dense and BM25 retrieval while keeping
    the original question intact for cross-encoder reranking.
    """
    expanded_terms = []
    seen = set()

    for pattern, terms in DOMAIN_EXPANSIONS.items():
        if re.search(pattern, question, flags=re.IGNORECASE):
            for term in terms:
                key = term.lower()
                if key not in seen:
                    seen.add(key)
                    expanded_terms.append(term)

    if not expanded_terms:
        return question

    expanded_query = question + " " + " ".join(expanded_terms)

    if verbose:
        print("\nQuery expansion applied:", flush=True)
        print(f"Original query: {question}", flush=True)
        print(f"Expanded query: {expanded_query}", flush=True)

    return expanded_query


# ==========================================
# 8. INITIALIZE BM25
# ==========================================

print("Building BM25 index...", flush=True)

tokenized_corpus = [
    tokenize(item.get("text", ""))
    for item in chunks
]

bm25 = BM25Okapi(tokenized_corpus)

print("BM25 index ready!", flush=True)

print(
    "Hybrid retrieval and reranking system initialized!",
    flush=True
)


# ==========================================
# 9. VECTOR SEARCH
# ==========================================

def vector_search(query, top_k=20):
    collection_count = collection.count()

    if collection_count == 0:
        return []

    query_embedding = model.encode(
        query,
        normalize_embeddings=True
    ).tolist()

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=min(top_k, collection_count)
    )

    retrieved_chunks = []

    if not results["documents"] or not results["documents"][0]:
        return retrieved_chunks

    for i in range(len(results["documents"][0])):
        retrieved_chunks.append({
            "id": results["ids"][0][i],
            "text": results["documents"][0][i],
            "metadata": (results["metadatas"][0][i] if results.get("metadatas") and results["metadatas"][0] else {}) or {},
            "distance": results["distances"][0][i] if results.get("distances") and results["distances"][0] else None,
        })

    return retrieved_chunks


# ==========================================
# 10. BM25 KEYWORD SEARCH
# ==========================================

def bm25_search(query, top_k=20):
    tokenized_query = tokenize(query)

    if not tokenized_query:
        return []

    scores = bm25.get_scores(tokenized_query)

    ranked_indices = sorted(
        range(len(scores)),
        key=lambda i: scores[i],
        reverse=True
    )

    retrieved_chunks = []

    for index in ranked_indices:
        if scores[index] <= 0:
            continue

        item = chunks[index]
        chunk_id = str(item.get("id") if item.get("id") is not None else index)

        retrieved_chunks.append({
            "id": chunk_id,
            "text": item.get("text", ""),
            "metadata": item.get("metadata") or {},
            "bm25_score": float(scores[index]),
        })

        if len(retrieved_chunks) >= top_k:
            break

    return retrieved_chunks


# ==========================================
# 11. RECIPROCAL RANK FUSION
# ==========================================

def reciprocal_rank_fusion(
    vector_results,
    bm25_results,
    top_k=5,
    candidate_k=CANDIDATE_K
):
    fused_results = {}

    for rank, result in enumerate(vector_results, start=1):
        chunk_id = str(result["id"])

        if chunk_id not in fused_results:
            fused_results[chunk_id] = {
                "id": chunk_id,
                "text": result["text"],
                "metadata": result.get("metadata") or {},
                "rrf_score": 0.0,
                "vector_rank": None,
                "bm25_rank": None,
            }

        fused_results[chunk_id]["rrf_score"] += 1 / (RRF_K + rank)
        fused_results[chunk_id]["vector_rank"] = rank
        fused_results[chunk_id]["distance"] = result.get("distance")

    for rank, result in enumerate(bm25_results, start=1):
        chunk_id = str(result["id"])

        if chunk_id not in fused_results:
            fused_results[chunk_id] = {
                "id": chunk_id,
                "text": result["text"],
                "metadata": result.get("metadata") or {},
                "rrf_score": 0.0,
                "vector_rank": None,
                "bm25_rank": None,
            }

        fused_results[chunk_id]["rrf_score"] += 1 / (RRF_K + rank)
        fused_results[chunk_id]["bm25_rank"] = rank
        fused_results[chunk_id]["bm25_score"] = result.get("bm25_score")

    ranked_results = sorted(
        fused_results.values(),
        key=lambda item: item["rrf_score"],
        reverse=True
    )

    return ranked_results[:candidate_k]


# ==========================================
# 12. CROSS-ENCODER RERANKING
# ==========================================

def rerank_results(
    question,
    candidates,
    top_k=5,
    verbose=False
):
    if verbose:
        print("\nReranking retrieved passages...", flush=True)

    if not candidates:
        return []

    pairs = [
        (question, candidate["text"])
        for candidate in candidates
    ]

    scores = reranker.predict(
        pairs,
        batch_size=32,
        show_progress_bar=False
    )

    reranked_results = []

    for candidate, score in zip(candidates, scores):
        item = candidate.copy()
        item["rerank_score"] = float(score)
        reranked_results.append(item)

    reranked_results.sort(
        key=lambda item: item["rerank_score"],
        reverse=True
    )

    return reranked_results[:top_k]


# ==========================================
# 13. FINAL RANKING DIAGNOSTICS
# ==========================================

def print_final_rankings(results):
    print("\n========== FINAL RETRIEVAL RANKINGS ==========", flush=True)

    if not results:
        print("No passages were retrieved.", flush=True)
        return

    for index, result in enumerate(results, start=1):
        metadata = result.get("metadata") or {}
        text = result.get("text", "")

        print(f"\nRank: {index}", flush=True)
        print(
            f"Document: {metadata.get('filename', metadata.get('source', 'Unknown'))}",
            flush=True
        )
        print(f"Category: {metadata.get('category', 'Unknown')}", flush=True)
        print(f"Page: {metadata.get('page', 'Unknown')}", flush=True)
        print(f"Rerank score: {result.get('rerank_score', 'N/A')}", flush=True)
        print(f"RRF score: {result.get('rrf_score', 'N/A')}", flush=True)
        print(
            f"Vector rank: {result.get('vector_rank', 'Not in vector results')}",
            flush=True
        )
        print(
            f"BM25 rank: {result.get('bm25_rank', 'Not in BM25 results')}",
            flush=True
        )
        print(f"Text preview: {text[:300]}", flush=True)
        print("-" * 60)


# ==========================================
# 14. COMPLETE HYBRID RETRIEVAL PIPELINE
# ==========================================

def hybrid_search(
    question,
    top_k=5,
    verbose=False
):
    """
    Retrieve and rerank veterinary passages.

    verbose=False hides internal retrieval diagnostics.
    verbose=True enables debugging output.
    """
    retrieval_query = expand_query(question, verbose=verbose)

    if verbose:
        print("\nPerforming dense retrieval...", flush=True)

    vector_results = vector_search(retrieval_query, top_k=20)

    if verbose:
        print("\nPerforming BM25 retrieval...", flush=True)

    sparse_results = bm25_search(retrieval_query, top_k=20)

    if verbose:
        print("\nCombining results using RRF...", flush=True)

    candidates = reciprocal_rank_fusion(
        vector_results,
        sparse_results,
        top_k=top_k,
        candidate_k=CANDIDATE_K
    )

    if verbose:
        print(f"RRF candidate pool: {len(candidates)} chunks", flush=True)

    final_results = rerank_results(
        question,
        candidates,
        top_k=top_k,
        verbose=verbose
    )

    if verbose:
        print_final_rankings(final_results)
        print(f"\nRetrieved {len(final_results)} reranked passages.", flush=True)

    return final_results


# ==========================================
# 15. INTERACTIVE TESTING
# ==========================================

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("       CATTLE HEALTH - HYBRID RETRIEVAL")
    print("=" * 60)

    question = input("\nEnter your cattle-health question: ").strip()

    if not question:
        print("Please enter a valid question.")
    else:
        final_results = hybrid_search(question, top_k=5, verbose=True)

        print("\n" + "=" * 60)
        print("FINAL RERANKED RESULTS")
        print("=" * 60)

        for index, result in enumerate(final_results, start=1):
            print(f"\nResult {index}")
            print("Source:", (result.get("metadata") or {}).get("filename", "Unknown"))
            print("Category:", (result.get("metadata") or {}).get("category", "Unknown"))
            print("Page:", (result.get("metadata") or {}).get("page", "Unknown"))
            print("Reranking Score:", round(result["rerank_score"], 4))
            print("RRF Score:", round(result["rrf_score"], 6))
            print("Vector Rank:", result.get("vector_rank"))
            print("BM25 Rank:", result.get("bm25_rank"))
            print("Text:", result["text"][:600])
            print("-" * 60)

import os
import json
import re
import chromadb

from pathlib import Path
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


# ==========================================
# 2. LAZY-LOADED RESOURCES (SAVES 600MB RAM ON BOOT)
# ==========================================

_model = None
_reranker = None
_client = None
_collection = None
_chunks = None
_bm25 = None

def _get_model():
    global _model
    if _model is None:
        print("[RAG] Loading embedding model on demand...", flush=True)
        from sentence_transformers import SentenceTransformer
        _model = SentenceTransformer(MODEL_NAME)
    return _model

def _get_reranker():
    global _reranker
    if os.getenv("DISABLE_RERANKER", "true").lower() in {"1", "true", "yes"}:
        return None
    if _reranker is None:
        try:
            print("[RAG] Loading cross-encoder reranker on demand...", flush=True)
            from sentence_transformers import CrossEncoder
            _reranker = CrossEncoder(RERANKER_NAME)
        except Exception as e:
            print(f"[RAG] Skipping cross-encoder reranker to save RAM: {e}", flush=True)
            _reranker = None
    return _reranker

def _get_collection():
    global _client, _collection
    if _collection is None:
        if not DB_PATH.exists():
            return None
        _client = chromadb.PersistentClient(path=str(DB_PATH))
        _collection = _client.get_or_create_collection(name=COLLECTION_NAME)
    return _collection

def _get_chunks():
    global _chunks
    if _chunks is None:
        _chunks = []
        if CHUNKS_FILE.exists():
            with open(CHUNKS_FILE, "r", encoding="utf-8") as file:
                for line in file:
                    if line.strip():
                        _chunks.append(json.loads(line))
    return _chunks

def _get_bm25():
    global _bm25
    if _bm25 is None:
        chunks_list = _get_chunks()
        tokenized_corpus = [tokenize(item["text"]) for item in chunks_list]
        _bm25 = BM25Okapi(tokenized_corpus)
    return _bm25


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

    words = re.findall(r"\b\w+\b", text.lower())

    return [
        word for word in words
        if word not in STOP_WORDS
    ]


# ==========================================
# 7. QUERY EXPANSION
# ==========================================

def expand_query(question, verbose=False):
    """
    Expand recognised cattle-health abbreviations
    into their full forms and related terminology.

    The original question is retained for reranking.

    Expansion is used only for dense and BM25 retrieval.
    """

    expanded_terms = []

    # BCS expansion

    if re.search(r"\bbcs\b", question, flags=re.IGNORECASE):

        expanded_terms.extend([
            "body condition score",
            "body condition scoring",
            "body condition assessment",
            "condition score in dairy cattle",
            "cow body condition",
            "body reserves",
            "fat cover",
            "tailhead",
            "loin",
            "BCS scale"
        ])

    if not expanded_terms:
        return question

    expanded_query = question + " " + " ".join(expanded_terms)

    if verbose:

        print("\nQuery expansion applied:", flush=True)

        print(
            f"Original query: {question}",
            flush=True
        )

        print(
            f"Expanded query: {expanded_query}",
            flush=True
        )

    return expanded_query


# ==========================================
# 8. VECTOR SEARCH
# ==========================================

def vector_search(query, top_k=20):
    coll = _get_collection()
    if coll is None:
        return []

    collection_count = coll.count()
    if collection_count == 0:
        return []

    model_inst = _get_model()
    query_embedding = model_inst.encode(
        query,
        normalize_embeddings=True
    ).tolist()

    results = coll.query(
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
            "metadata": results["metadatas"][0][i],
            "distance": results["distances"][0][i]
        })

    return retrieved_chunks


# ==========================================
# 9. BM25 KEYWORD SEARCH
# ==========================================

def bm25_search(query, top_k=20):
    tokenized_query = tokenize(query)
    if not tokenized_query:
        return []

    bm25_inst = _get_bm25()
    scores = bm25_inst.get_scores(tokenized_query)

    ranked_indices = sorted(
        range(len(scores)),
        key=lambda i: scores[i],
        reverse=True
    )

    chunks_list = _get_chunks()
    retrieved_chunks = []

    for index in ranked_indices:
        if scores[index] <= 0:
            continue

        item = chunks_list[index]
        retrieved_chunks.append({
            "id": item["id"],
            "text": item["text"],
            "metadata": item["metadata"],
            "bm25_score": float(scores[index])
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

    # Process vector rankings

    for rank, result in enumerate(vector_results, start=1):

        chunk_id = result["id"]

        if chunk_id not in fused_results:

            fused_results[chunk_id] = {
                "id": chunk_id,
                "text": result["text"],
                "metadata": result["metadata"],
                "rrf_score": 0.0,
                "vector_rank": None,
                "bm25_rank": None
            }

        fused_results[chunk_id]["rrf_score"] += (
            1 / (RRF_K + rank)
        )

        fused_results[chunk_id]["vector_rank"] = rank

        fused_results[chunk_id]["distance"] = (
            result["distance"]
        )

    # Process BM25 rankings

    for rank, result in enumerate(bm25_results, start=1):

        chunk_id = result["id"]

        if chunk_id not in fused_results:

            fused_results[chunk_id] = {
                "id": chunk_id,
                "text": result["text"],
                "metadata": result["metadata"],
                "rrf_score": 0.0,
                "vector_rank": None,
                "bm25_rank": None
            }

        fused_results[chunk_id]["rrf_score"] += (
            1 / (RRF_K + rank)
        )

        fused_results[chunk_id]["bm25_rank"] = rank

        fused_results[chunk_id]["bm25_score"] = (
            result["bm25_score"]
        )

    # Rank by RRF score

    ranked_results = sorted(
        fused_results.values(),
        key=lambda item: item["rrf_score"],
        reverse=True
    )

    candidates = ranked_results[:candidate_k]

    return candidates


# ==========================================
# 12. CROSS-ENCODER RERANKING
# ==========================================

def rerank_results(
    question,
    candidates,
    top_k=5,
    verbose=False
):

    if not candidates:
        return []

    reranker_inst = _get_reranker()
    if reranker_inst is not None:
        if verbose:
            print(
                "\nReranking retrieved passages with CrossEncoder...",
                flush=True
            )

        pairs = [
            (question, candidate["text"])
            for candidate in candidates
        ]

        scores = reranker_inst.predict(
            pairs,
            batch_size=16,
            show_progress_bar=False
        )

        reranked_results = []

        for candidate, score in zip(candidates, scores):

            candidate = candidate.copy()

            candidate["rerank_score"] = float(score)

            reranked_results.append(candidate)

        reranked_results.sort(
            key=lambda item: item["rerank_score"],
            reverse=True
        )

        return reranked_results[:top_k]
    else:
        # High-efficiency RRF ranking (saves 250MB RAM on free servers)
        for candidate in candidates:
            candidate["rerank_score"] = candidate.get("rrf_score", 0.0)
        return candidates[:top_k]


# ==========================================
# 13. FINAL RANKING DIAGNOSTICS
# ==========================================

def print_final_rankings(results):

    print(
        "\n========== FINAL RETRIEVAL RANKINGS ==========",
        flush=True
    )

    if not results:

        print(
            "No passages were retrieved.",
            flush=True
        )

        return

    for index, result in enumerate(results, start=1):

        metadata = result.get("metadata", {})

        text = result.get("text", "")

        print(f"\nRank: {index}", flush=True)

        print(
            f"Document: {metadata.get('filename', metadata.get('source', 'Unknown'))}",
            flush=True
        )

        print(
            f"Category: {metadata.get('category', 'Unknown')}",
            flush=True
        )

        print(
            f"Page: {metadata.get('page', 'Unknown')}",
            flush=True
        )

        print(
            f"Rerank score: {result.get('rerank_score', 'N/A')}",
            flush=True
        )

        print(
            f"RRF score: {result.get('rrf_score', 'N/A')}",
            flush=True
        )

        print(
            f"Vector rank: {result.get('vector_rank', 'Not in vector results')}",
            flush=True
        )

        print(
            f"BM25 rank: {result.get('bm25_rank', 'Not in BM25 results')}",
            flush=True
        )

        print(
            f"Text preview: {text[:300]}",
            flush=True
        )

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

    retrieval_query = expand_query(
        question,
        verbose=verbose
    )

    # Dense retrieval

    if verbose:
        print(
            "\nPerforming dense retrieval...",
            flush=True
        )

    vector_results = vector_search(
        retrieval_query,
        top_k=20
    )

    # Sparse retrieval

    if verbose:
        print(
            "\nPerforming BM25 retrieval...",
            flush=True
        )

    sparse_results = bm25_search(
        retrieval_query,
        top_k=20
    )

    # Reciprocal Rank Fusion

    if verbose:
        print(
            "\nCombining results using RRF...",
            flush=True
        )

    candidates = reciprocal_rank_fusion(
        vector_results,
        sparse_results,
        top_k=top_k,
        candidate_k=CANDIDATE_K
    )

    if verbose:

        print(
            f"RRF candidate pool: {len(candidates)} chunks",
            flush=True
        )

    # CrossEncoder reranking

    final_results = rerank_results(
        question,
        candidates,
        top_k=top_k,
        verbose=verbose
    )

    if verbose:

        print_final_rankings(final_results)

        print(
            f"\nRetrieved {len(final_results)} reranked passages.",
            flush=True
        )

    return final_results


# ==========================================
# 15. INTERACTIVE TESTING
# ==========================================

if __name__ == "__main__":

    print("\n" + "=" * 60)

    print(
        "       CATTLE HEALTH - HYBRID RETRIEVAL"
    )

    print("=" * 60)

    question = input(
        "\nEnter your cattle-health question: "
    ).strip()

    if not question:

        print("Please enter a valid question.")

    else:

        final_results = hybrid_search(
            question,
            top_k=5,
            verbose=True
        )

        print("\n" + "=" * 60)

        print("FINAL RERANKED RESULTS")

        print("=" * 60)

        for index, result in enumerate(final_results, start=1):

            print(f"\nResult {index}")

            print(
                "Source:",
                result["metadata"].get(
                    "filename",
                    "Unknown"
                )
            )

            print(
                "Category:",
                result["metadata"].get(
                    "category",
                    "Unknown"
                )
            )

            print(
                "Page:",
                result["metadata"].get(
                    "page",
                    "Unknown"
                )
            )

            print(
                "Reranking Score:",
                round(
                    result["rerank_score"],
                    4
                )
            )

            print(
                "RRF Score:",
                round(
                    result["rrf_score"],
                    6
                )
            )

            print(
                "Vector Rank:",
                result["vector_rank"]
            )

            print(
                "BM25 Rank:",
                result["bm25_rank"]
            )

            print(
                "Text:",
                result["text"][:600]
            )

            print("-" * 60)
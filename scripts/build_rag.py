"""
build_rag.py
-------------
Indexes all documents into FAISS vector stores.

  Index              Source
  ─────────────────  ─────────────────────────────────────
  policies/          rag/policies/*.md
  repair_catalog/    rag/repair_catalog/repair_costs.json
  fraud_rules/       rag/fraud_rules/fraud_rules.json
  claims_history/    rag/claims_history/historical_claims.json

Embeddings:
  - If GEMINI_API_KEY is valid  -> Google text-embedding-004 (best quality)
  - Otherwise                   -> Local TF-IDF + SVD fallback (no API needed)

Run: python scripts/build_rag.py
"""

import json
import pickle
import sys
from pathlib import Path

import numpy as np
import faiss

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from app.core.config import settings
import google.generativeai as genai

INDEX_BASE = Path(settings.chroma_persist_dir)
EMBEDDING_DIM = 768

# Global state for embedder
USE_GEMINI = False
_tfidf_vec = None
_tfidf_svd = None
_tfidf_fitted = False


# ─────────────────────────────────────────────────────────────
#  Configure
# ─────────────────────────────────────────────────────────────

def configure():
    global USE_GEMINI
    key = settings.gemini_api_key
    if key and key != "your_gemini_api_key_here":
        genai.configure(api_key=key)
        USE_GEMINI = True
        print("Gemini API configured - using text-embedding-004")
    else:
        USE_GEMINI = False
        print("No valid GEMINI_API_KEY - using local TF-IDF fallback embeddings.")
        print("RAG will work; quality improves with a real Gemini key.")


# ─────────────────────────────────────────────────────────────
#  Local fallback embedder
# ─────────────────────────────────────────────────────────────

def _fit_local(corpus):
    global _tfidf_vec, _tfidf_svd, _tfidf_fitted
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.decomposition import TruncatedSVD
    n = min(EMBEDDING_DIM, len(corpus) - 1, 500)
    _tfidf_vec = TfidfVectorizer(max_features=10000, ngram_range=(1, 2))
    mat = _tfidf_vec.fit_transform(corpus)
    _tfidf_svd = TruncatedSVD(n_components=n, random_state=42)
    reduced = _tfidf_svd.fit_transform(mat).astype(np.float32)
    if reduced.shape[1] < EMBEDDING_DIM:
        pad = np.zeros((reduced.shape[0], EMBEDDING_DIM - reduced.shape[1]), dtype=np.float32)
        reduced = np.hstack([reduced, pad])
    _tfidf_fitted = True
    return reduced.tolist()


def _transform_local(texts):
    mat = _tfidf_vec.transform(texts)
    reduced = _tfidf_svd.transform(mat).astype(np.float32)
    if reduced.shape[1] < EMBEDDING_DIM:
        pad = np.zeros((reduced.shape[0], EMBEDDING_DIM - reduced.shape[1]), dtype=np.float32)
        reduced = np.hstack([reduced, pad])
    return reduced.tolist()


# ─────────────────────────────────────────────────────────────
#  Embed dispatcher
# ─────────────────────────────────────────────────────────────

def embed_batch(texts, task_type="retrieval_document"):
    if USE_GEMINI:
        embeddings = []
        batch_size = 20
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            result = genai.embed_content(
                model="models/text-embedding-004",
                content=batch,
                task_type=task_type,
            )
            embeddings.extend(result["embedding"])
            print(f"    Embedded {min(i + batch_size, len(texts))}/{len(texts)}")
        return embeddings
    else:
        if not _tfidf_fitted:
            print(f"    Fitting local embedder on {len(texts)} docs...")
            return _fit_local(texts)
        return _transform_local(texts)


# ─────────────────────────────────────────────────────────────
#  Chunking
# ─────────────────────────────────────────────────────────────

def chunk_text(text, chunk_size=400, overlap=80):
    words = text.split()
    chunks, start = [], 0
    while start < len(words):
        chunks.append(" ".join(words[start:start + chunk_size]))
        start += chunk_size - overlap
    return [c for c in chunks if len(c.strip()) > 50]


# ─────────────────────────────────────────────────────────────
#  Save FAISS index
# ─────────────────────────────────────────────────────────────

def save_index(name, embeddings, documents, metadatas):
    index_dir = INDEX_BASE / name
    index_dir.mkdir(parents=True, exist_ok=True)
    vectors = np.array(embeddings, dtype=np.float32)
    dim = vectors.shape[1]
    index = faiss.IndexFlatL2(dim)
    index.add(vectors)
    faiss.write_index(index, str(index_dir / "index.faiss"))
    with open(index_dir / "docs.pkl", "wb") as f:
        pickle.dump({"documents": documents, "metadatas": metadatas}, f)
    print(f"  Saved {len(documents)} vectors -> {index_dir}")


# ─────────────────────────────────────────────────────────────
#  1. Policies
# ─────────────────────────────────────────────────────────────

def index_policies():
    print("\nIndexing insurance policies...")
    policy_dir = ROOT / "rag" / "policies"
    meta_path = policy_dir / "policy_metadata.json"
    policy_meta = {}
    if meta_path.exists():
        with open(meta_path, "r", encoding="utf-8") as f:
            for p in json.load(f):
                policy_meta[p["id"]] = p

    docs, metas = [], []
    for md_file in sorted(policy_dir.glob("policy_*.md")):
        policy_id = md_file.stem.replace("policy_", "").upper()
        meta_info = policy_meta.get(policy_id, {})
        with open(md_file, "r", encoding="utf-8") as f:
            content = f.read()
        sections = content.split("\n## ")
        for i, section in enumerate(sections):
            for j, chunk in enumerate(chunk_text(section.strip(), chunk_size=250)):
                docs.append(chunk)
                metas.append({
                    "source": md_file.name,
                    "policy_id": policy_id,
                    "policy_number": meta_info.get("prefix", "POL-" + policy_id),
                    "clause_id": "Section {}.{}".format(i, j),
                    "deductible": meta_info.get("deductible", 5000),
                    "max_payout": meta_info.get("max_payout", 100000),
                    "coverage_pct": meta_info.get("coverage_pct", 80),
                })
        print("  {} processed".format(md_file.name))

    if not docs:
        print("  No policy files found - run generate_datasets.py first")
        return
    embs = embed_batch(docs)
    save_index("policies", embs, docs, metas)
    print("  Policies indexed: {} chunks".format(len(docs)))


# ─────────────────────────────────────────────────────────────
#  2. Repair catalog
# ─────────────────────────────────────────────────────────────

def index_repair_catalog():
    print("\nIndexing repair catalog...")
    catalog_path = ROOT / "rag" / "repair_catalog" / "repair_costs.json"
    if not catalog_path.exists():
        print("  repair_costs.json not found - skipping")
        return
    with open(catalog_path, "r", encoding="utf-8") as f:
        catalog = json.load(f)
    docs, metas = [], []
    for vehicle, parts in catalog.get("vehicles", {}).items():
        for part_name, cost in parts.items():
            total = cost.get("parts_cost", 0) + cost.get("labour_cost", 0)
            doc = (
                "Vehicle: {}. Part: {}. Action: {}. "
                "Parts cost: INR {}. Labour cost: INR {}. Total: INR {}.".format(
                    vehicle, part_name, cost.get("action", "REPAIR"),
                    cost.get("parts_cost", 0), cost.get("labour_cost", 0), total
                )
            )
            docs.append(doc)
            metas.append({
                "vehicle": vehicle, "part_name": part_name,
                "action": cost.get("action", "REPAIR"),
                "parts_cost": cost.get("parts_cost", 0),
                "labour_cost": cost.get("labour_cost", 0),
                "total_cost": total,
            })
    embs = embed_batch(docs)
    save_index("repair_catalog", embs, docs, metas)
    print("  Repair catalog indexed: {} entries".format(len(docs)))


# ─────────────────────────────────────────────────────────────
#  3. Fraud rules
# ─────────────────────────────────────────────────────────────

def index_fraud_rules():
    print("\nIndexing fraud rules...")
    rules_path = ROOT / "rag" / "fraud_rules" / "fraud_rules.json"
    if not rules_path.exists():
        print("  fraud_rules.json not found - skipping")
        return
    with open(rules_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    docs, metas = [], []
    for rule in data.get("rules", []):
        doc = (
            "Fraud Rule [{}]: {}. Description: {}. "
            "Category: {}. Risk weight: {:.0%}.".format(
                rule["id"], rule["name"], rule["description"],
                rule.get("category", "General"), rule.get("weight", 0.5)
            )
        )
        docs.append(doc)
        metas.append({
            "rule_id": rule["id"], "name": rule["name"],
            "category": rule.get("category", "General"),
            "weight": rule.get("weight", 0.5),
        })
    embs = embed_batch(docs)
    save_index("fraud_rules", embs, docs, metas)
    print("  Fraud rules indexed: {} rules".format(len(docs)))


# ─────────────────────────────────────────────────────────────
#  4. Claims history
# ─────────────────────────────────────────────────────────────

def index_claims_history():
    print("\nIndexing claims history...")
    claims_path = ROOT / "rag" / "claims_history" / "historical_claims.json"
    if not claims_path.exists():
        print("  historical_claims.json not found - skipping")
        return
    with open(claims_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    docs, metas = [], []
    for claim in data.get("claims", []):
        doc = (
            "Claim {}: {} ({} policy). Damage: {}. Severity: {}. "
            "Parts: {}. Cost: INR {}. Decision: {}. Fraud: {}. {}".format(
                claim["claim_id"], claim["vehicle_full"], claim["policy_type"],
                claim["damage_type"], claim["severity"],
                ", ".join(claim.get("damaged_parts", [])),
                claim["estimated_repair_cost"], claim["final_decision"],
                claim["fraud_risk"], claim["claim_description"]
            )
        )
        docs.append(doc)
        metas.append({
            "claim_id": claim["claim_id"],
            "vehicle": claim["vehicle_full"],
            "policy_type": claim["policy_type"],
            "damage_type": claim["damage_type"],
            "severity": claim["severity"],
            "repair_cost": claim["estimated_repair_cost"],
            "decision": claim["final_decision"],
            "fraud_risk": claim["fraud_risk"],
        })
    # Claims need local embedder fitted first (large corpus)
    embs = embed_batch(docs)
    save_index("claims_history", embs, docs, metas)
    print("  Claims history indexed: {} claims".format(len(docs)))


# ─────────────────────────────────────────────────────────────
#  MAIN
# ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("\nClaimSense AI - Building RAG Knowledge Base (FAISS)")
    print("=" * 55)
    configure()
    index_policies()
    index_repair_catalog()
    index_fraud_rules()
    index_claims_history()
    print("\nRAG knowledge base built successfully.")
    print("Index directory:", INDEX_BASE)
    print("\nIndexes created:")
    for d in sorted(INDEX_BASE.iterdir()):
        if d.is_dir():
            idx_file = d / "index.faiss"
            docs_file = d / "docs.pkl"
            if idx_file.exists() and docs_file.exists():
                with open(docs_file, "rb") as f:
                    n = len(pickle.load(f)["documents"])
                print("  {}: {} documents".format(d.name, n))
    print("\nNext step: uvicorn app.main:app --reload --port 8000")

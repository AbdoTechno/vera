from typing import List, Dict, Any, Optional
from src.embeddings.vector_store import VectorStoreManager
from src.retrieval.query_expansion import MedicalQueryExpander
from src.utils.logger import logger

class HybridRetriever:
    """Combines BM25 Keyword Search Retreival with SemanticSearch Dense Vector Search using Reciprocal Rank Fusion (RRF)."""

    def __init__(
        self,
        vector_store: VectorStoreManager,
        all_chunks: Optional[List[Dict[str, Any]]] = None,
        dense_weight: float = 0.7,
        bm25_weight: float = 0.3,
        use_expansion: bool = True
    ):
        self.vector_store = vector_store
        self.dense_weight = dense_weight
        self.bm25_weight = bm25_weight
        self.use_expansion = use_expansion
        self.expander = MedicalQueryExpander() if use_expansion else None
        
        self.chunks_corpus = all_chunks or []
        self.bm25 = None
        if self.chunks_corpus:
            self._init_bm25()

    def _init_bm25(self):
        """Initializes BM25 index on chunk contents.
        -  `BM25 (Best Matching 25)` is a Keyword Retriever Method that ranks documents based on term frequency 
        and inverse document frequency similar to TF-IDF but optimized for ranking."""
        try:
            from rank_bm25 import BM25Okapi
            tokenized_corpus = [c["content"].lower().split() for c in self.chunks_corpus]
            self.bm25 = BM25Okapi(tokenized_corpus)
            logger.info(f"Initialized BM25 index with {len(self.chunks_corpus)} documents.")
        except ImportError:
            logger.warning("rank_bm25 not installed. HybridRetriever will rely on dense retrieval.")

    def retrieve(
        self,
        query: str,
        top_k: int = 4,
        doc_filter: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Executes hybrid retrieval combining dense vector search and BM25 with optional document scoping."""
        search_query = self.expander.expand(query) if self.expander else query
        
        # Determine metadata filter if doc_filter is provided
        where_filter = None
        if doc_filter:
            clean_filter = doc_filter.strip()
            if clean_filter.startswith("DOC_"):
                where_filter = {"doc_id": clean_filter}
            else:
                where_filter = {"doc_name": clean_filter}
        
        # 1. Dense search with filter
        dense_results = self.vector_store.search(search_query, top_k=top_k * 2, where=where_filter)

        # If BM25 is not initialized or corpus empty, return dense results
        if not self.bm25 or not self.chunks_corpus:
            return dense_results[:top_k]

        # 2. BM25 keyword search
        tokenized_query = search_query.lower().split()
        bm25_scores = self.bm25.get_scores(tokenized_query)
        
        # Filter and rank BM25 results
        valid_indices = []
        for i, score in enumerate(bm25_scores):
            if doc_filter:
                chunk = self.chunks_corpus[i]
                c_doc_id = str(chunk.get("doc_id", "")).strip()
                c_doc_name = str(chunk.get("doc_name", "")).strip()
                if doc_filter != c_doc_id and doc_filter != c_doc_name:
                    continue
            valid_indices.append(i)

        bm25_ranked_indices = sorted(valid_indices, key=lambda i: bm25_scores[i], reverse=True)[:top_k * 2]
        
        # 3. Reciprocal Rank Fusion (RRF)
        rrf_scores: Dict[str, float] = {}
        chunk_map: Dict[str, Dict[str, Any]] = {}

        # Dense ranking
        for rank, item in enumerate(dense_results):
            meta = item.get("metadata", {})
            cid = meta.get("chunk_id") or f"{meta.get('doc_id')}_{meta.get('page_number')}_{hash(item.get('content', ''))}"
            chunk_map[cid] = item
            rrf_scores[cid] = rrf_scores.get(cid, 0.0) + (self.dense_weight / (60 + rank + 1))

        # BM25 ranking
        for rank, idx in enumerate(bm25_ranked_indices):
            chunk = self.chunks_corpus[idx]
            cid = chunk.get("chunk_id") or f"{chunk.get('doc_id')}_{chunk.get('page_number')}_{hash(chunk.get('content', ''))}"
            if cid not in chunk_map:
                max_score = max(bm25_scores) if max(bm25_scores) > 0 else 1.0
                chunk_map[cid] = {
                    "content": chunk.get("content"),
                    "metadata": {
                        "chunk_id": chunk.get("chunk_id"),
                        "doc_id": chunk.get("doc_id"),
                        "doc_name": chunk.get("doc_name"),
                        "section": chunk.get("section"),
                        "page_number": chunk.get("page_number")
                    },
                    "similarity_score": round(float(bm25_scores[idx] / max_score), 4)
                }

            rrf_scores[cid] = rrf_scores.get(cid, 0.0) + (self.bm25_weight / (60 + rank + 1))

        # Sort by combined RRF score
        sorted_cids = sorted(rrf_scores.keys(), key=lambda k: rrf_scores[k], reverse=True)
        final_results = [chunk_map[cid] for cid in sorted_cids[:top_k]]

        scope_tag = f" (scoped to '{doc_filter}')" if doc_filter else ""
        logger.info(f"Hybrid retrieval completed{scope_tag}: returned top {len(final_results)} chunks.")
        return final_results


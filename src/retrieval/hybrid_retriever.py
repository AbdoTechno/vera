from typing import List, Dict, Any, Optional
from src.embeddings.vector_store import VectorStoreManager
from src.retrieval.query_expansion import MedicalQueryExpander
from src.utils.logger import logger

class HybridRetriever:
    """Combines BM25 Keyword Search with Dense Vector Search using Reciprocal Rank Fusion (RRF)."""

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
        """Initializes BM25 index on chunk contents."""
        try:
            from rank_bm25 import BM25Okapi
            tokenized_corpus = [c["content"].lower().split() for c in self.chunks_corpus]
            self.bm25 = BM25Okapi(tokenized_corpus)
            logger.info(f"Initialized BM25 index with {len(self.chunks_corpus)} documents.")
        except ImportError:
            logger.warning("rank_bm25 not installed. HybridRetriever will rely on dense retrieval.")

    def retrieve(self, query: str, top_k: int = 4) -> List[Dict[str, Any]]:
        """Executes hybrid retrieval combining dense vector search and BM25."""
        search_query = self.expander.expand(query) if self.expander else query
        
        # 1. Dense search
        dense_results = self.vector_store.search(search_query, top_k=top_k * 2)

        # If BM25 is not initialized or corpus empty, return dense results
        if not self.bm25 or not self.chunks_corpus:
            return dense_results[:top_k]

        # 2. BM25 keyword search
        tokenized_query = search_query.lower().split()
        bm25_scores = self.bm25.get_scores(tokenized_query)
        
        # Rank BM25 results
        bm25_ranked_indices = sorted(range(len(bm25_scores)), key=lambda i: bm25_scores[i], reverse=True)[:top_k * 2]
        
        # 3. Reciprocal Rank Fusion (RRF)
        rrf_scores: Dict[str, float] = {}
        chunk_map: Dict[str, Dict[str, Any]] = {}

        # Dense ranking
        for rank, item in enumerate(dense_results):
            cid = f"{item['metadata'].get('doc_id')}_{item['metadata'].get('page_number')}_{item['content'][:30]}"
            chunk_map[cid] = item
            rrf_scores[cid] = rrf_scores.get(cid, 0.0) + (self.dense_weight / (60 + rank + 1))

        # BM25 ranking
        for rank, idx in enumerate(bm25_ranked_indices):
            chunk = self.chunks_corpus[idx]
            cid = f"{chunk.get('doc_id')}_{chunk.get('page_number')}_{chunk.get('content')[:30]}"
            if cid not in chunk_map:
                chunk_map[cid] = {
                    "content": chunk.get("content"),
                    "metadata": {
                        "doc_id": chunk.get("doc_id"),
                        "doc_name": chunk.get("doc_name"),
                        "section": chunk.get("section"),
                        "page_number": chunk.get("page_number")
                    },
                    "similarity_score": round(float(bm25_scores[idx] / (max(bm25_scores) + 1e-6)), 4)
                }
            rrf_scores[cid] = rrf_scores.get(cid, 0.0) + (self.bm25_weight / (60 + rank + 1))

        # Sort by combined RRF score
        sorted_cids = sorted(rrf_scores.keys(), key=lambda k: rrf_scores[k], reverse=True)
        final_results = [chunk_map[cid] for cid in sorted_cids[:top_k]]

        logger.info(f"Hybrid retrieval completed: returned top {len(final_results)} chunks.")
        return final_results

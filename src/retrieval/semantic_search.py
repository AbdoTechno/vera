from typing import List, Dict, Any, Optional
from src.embeddings.vector_store import VectorStoreManager
from src.utils.logger import logger

class SemanticSearchEngine:
    """Performs semantic vector search with similarity filtering and metadata formatting."""

    def __init__(self, vector_store: VectorStoreManager, similarity_threshold: float = 0.60):
        self.vector_store = vector_store
        self.similarity_threshold = similarity_threshold

    def retrieve(self, query: str, top_k: int = 4) -> List[Dict[str, Any]]:
        """Retrieves Top-K relevant chunks above the similarity threshold."""
        logger.info(f"Retrieving top {top_k} results for query: '{query}'")
        raw_results = self.vector_store.search(query, top_k=top_k)
        
        filtered_results = []
        for r in raw_results:
            score = r.get("similarity_score", 0.0)
            if score >= self.similarity_threshold:
                filtered_results.append(r)
            else:
                logger.debug(f"Filtered out chunk due to low similarity ({score:.4f} < {self.similarity_threshold})")

        logger.info(f"Retrieved {len(filtered_results)} valid chunks (out of {len(raw_results)} candidates).")
        return filtered_results

import os
from typing import List, Dict, Any, Optional
from pathlib import Path
from src.ingestion.chunker import Chunk
from src.embeddings.embedder import MedicalEmbedder
from src.utils.logger import logger

class VectorStoreManager:
    """Manages persistent vector indexing and similarity queries using ChromaDB or in-memory fallback."""

    def __init__(
        self,
        persist_dir: str = "./data/vector_db",
        collection_name: str = "vera_clinical_guidelines",
        embedder: Optional[MedicalEmbedder] = None,
        reset_collection: bool = False
    ):
        self.persist_dir = persist_dir
        self.collection_name = collection_name
        self.embedder = embedder or MedicalEmbedder()
        self.client = None
        self.collection = None
        self._in_memory_docs: List[Dict[str, Any]] = []
        
        self._init_store(reset=reset_collection)

    def _init_store(self, reset: bool = False):
        try:
            import chromadb
            os.makedirs(self.persist_dir, exist_ok=True)
            self.client = chromadb.PersistentClient(path=self.persist_dir)
            
            if reset:
                try:
                    self.client.delete_collection(self.collection_name)
                    logger.info(f"Reset existing ChromaDB collection: '{self.collection_name}'")
                except Exception:
                    pass

            self.collection = self.client.get_or_create_collection(
                name=self.collection_name,
                metadata={"hnsw:space": "cosine"}
            )
            logger.info(f"VectorStoreManager connected to ChromaDB collection: '{self.collection_name}' (Current count: {self.collection.count()})")
        except ImportError:
            logger.warning("chromadb not installed. VectorStoreManager will use in-memory store fallback.")

    def reset(self):
        """Deletes and recreates the collection to accommodate new embedding models or dimensions."""
        if self.client:
            try:
                self.client.delete_collection(self.collection_name)
            except Exception:
                pass
            self.collection = self.client.get_or_create_collection(
                name=self.collection_name,
                metadata={"hnsw:space": "cosine"}
            )
            logger.info(f"Successfully reset collection: '{self.collection_name}'")

    def index_chunks(self, chunks: List[Chunk], batch_size: int = 64) -> int:
        """Indexes a list of structured Chunk objects into ChromaDB, auto-handling dimension changes."""
        if not chunks:
            logger.warning("No chunks provided to index.")
            return 0

        logger.info(f"Indexing {len(chunks)} chunks into vector store...")
        
        if self.collection:
            for i in range(0, len(chunks), batch_size):
                batch = chunks[i:i + batch_size]
                ids = [f"{c.doc_id}_ch_{c.chunk_id}" for c in batch]
                documents = [c.content for c in batch]
                metadatas = [
                    {
                        "doc_id": c.doc_id,
                        "doc_name": c.doc_name,
                        "section": c.section,
                        "page_number": c.page_number,
                        "token_count": c.token_count
                    }
                    for c in batch
                ]
                embeddings = self.embedder.embed_texts(documents)

                try:
                    self.collection.upsert(
                        ids=ids,
                        documents=documents,
                        embeddings=embeddings,
                        metadatas=metadatas
                    )
                except Exception as e:
                    # Auto-handle dimension mismatch if user switched embedding model
                    if "dimension" in str(e).lower():
                        logger.warning(f"Dimension mismatch detected ({e}). Automatically recreating collection with new model dimensions...")
                        self.reset()
                        self.collection.upsert(
                            ids=ids,
                            documents=documents,
                            embeddings=embeddings,
                            metadatas=metadatas
                        )
                    else:
                        raise e

            count = self.collection.count()
            logger.info(f"Total records in ChromaDB: {count}")
            return count
        else:
            for c in chunks:
                self._in_memory_docs.append({
                    "content": c.content,
                    "metadata": {
                        "doc_id": c.doc_id,
                        "doc_name": c.doc_name,
                        "section": c.section,
                        "page_number": c.page_number
                    }
                })
            return len(self._in_memory_docs)

    def search(self, query: str, top_k: int = 4) -> List[Dict[str, Any]]:
        """Searches the vector store with dense embedding query."""
        if self.collection and self.collection.count() > 0:
            query_embedding = self.embedder.embed_query(query)
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=min(top_k, self.collection.count()),
                include=["documents", "metadatas", "distances"]
            )

            formatted_results = []
            if results and results.get("documents") and results["documents"][0]:
                docs = results["documents"][0]
                metas = results["metadatas"][0]
                distances = results["distances"][0]

                for doc, meta, dist in zip(docs, metas, distances):
                    similarity = 1.0 - dist if dist is not None else 0.0
                    formatted_results.append({
                        "content": doc,
                        "metadata": meta,
                        "distance": dist,
                        "similarity_score": round(similarity, 4)
                    })
            return formatted_results
        else:
            # Fallback search
            results = []
            for doc in self._in_memory_docs[:top_k]:
                results.append({
                    "content": doc["content"],
                    "metadata": doc["metadata"],
                    "similarity_score": 0.85
                })
            return results

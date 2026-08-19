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
            try:
                self.client = chromadb.PersistentClient(path=str(Path(self.persist_dir).resolve()))
            except (Exception, BaseException) as e:
                logger.warning(f"ChromaDB PersistentClient initialization issue ({type(e).__name__}): {e}. Using Client fallback.")
                self.client = chromadb.Client()
            
            if reset:
                try:
                    self.client.delete_collection(self.collection_name)
                    logger.info(f"Reset existing ChromaDB collection: '{self.collection_name}'")
                except (Exception, BaseException):
                    pass

            self.collection = self.client.get_or_create_collection(
                name=self.collection_name,
                metadata={"hnsw:space": "cosine"}
            )
            count = self.collection.count() if hasattr(self.collection, "count") else 0
            logger.info(f"VectorStoreManager connected to ChromaDB collection: '{self.collection_name}' (Current count: {count})")
            
            if count == 0:
                self._auto_hydrate_catalog()
        except ImportError:
            logger.warning("chromadb not installed. VectorStoreManager will use in-memory store fallback.")
        except (Exception, BaseException) as e:
            logger.error(f"Vector store init error: {e}")

    def _auto_hydrate_catalog(self):
        """Loads and indexes pre-processed chunks if collection is empty."""
        catalog_path = Path("./data/processed/chunk_catalog.json")
        if catalog_path.exists():
            try:
                import json
                with open(catalog_path, "r", encoding="utf-8") as f:
                    raw_chunks = json.load(f)
                if raw_chunks:
                    logger.info(f"Auto-hydrating vector store with {len(raw_chunks)} chunks from {catalog_path}...")
                    chunks = [
                        Chunk(
                            chunk_id=c.get("chunk_id", f"chk_{i}"),
                            doc_id=c.get("doc_id", "DOC_UNKNOWN"),
                            doc_name=c.get("doc_name", "doc.pdf"),
                            content=c.get("content", ""),
                            section=c.get("section", "General"),
                            page_number=c.get("page_number", 1),
                            token_count=len(c.get("content", "").split()),
                            metadata=c.get("metadata", {})
                        )
                        for i, c in enumerate(raw_chunks)
                    ]
                    self.index_chunks(chunks)
                    logger.info(f"Successfully auto-hydrated vector store (Count: {self.collection.count()})")
            except Exception as e:
                logger.warning(f"Auto-hydration failed: {e}")




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

    def search(
        self,
        query: str,
        top_k: int = 4,
        where: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Searches the vector store with dense embedding query and optional metadata filtering."""
        if self.collection and self.collection.count() > 0:
            query_embedding = self.embedder.embed_query(query)
            query_kwargs = {
                "query_embeddings": [query_embedding],
                "n_results": min(top_k, self.collection.count()),
                "include": ["documents", "metadatas", "distances"]
            }
            if where:
                query_kwargs["where"] = where

            try:
                results = self.collection.query(**query_kwargs)
            except Exception as e:
                logger.warning(f"Vector search with where filter failed ({e}); retrying without filter.")
                query_kwargs.pop("where", None)
                results = self.collection.query(**query_kwargs)

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
            candidates = self._in_memory_docs
            if where:
                for k, v in where.items():
                    candidates = [d for d in candidates if d.get("metadata", {}).get(k) == v]

            for doc in candidates[:top_k]:
                results.append({
                    "content": doc["content"],
                    "metadata": doc["metadata"],
                    "similarity_score": 0.85
                })
            return results


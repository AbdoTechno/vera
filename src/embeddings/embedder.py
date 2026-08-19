import os
import warnings
from typing import List, Union, Optional
from src.utils.logger import logger

# Suppress sentence-transformers dimension rename FutureWarnings
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)

class MedicalEmbedder:
    """Generates dense vector embeddings using Google Gemini API or HuggingFace SentenceTransformers."""

    MODEL_ALIASES = {
        "gemini": "models/text-embedding-004",
        "text-embedding-004": "models/text-embedding-004",
        "multilingual-e5-large": "intfloat/multilingual-e5-large",
        "multilingual-e5-base": "intfloat/multilingual-e5-base",
        "multilingual-e5-small": "intfloat/multilingual-e5-small",
        "e5-small": "intfloat/e5-small-v2",
        "bge-base": "BAAI/bge-base-en-v1.5",
        "bge-small": "BAAI/bge-small-en-v1.5",
        "minilm": "sentence-transformers/all-MiniLM-L6-v2"
    }

    def __init__(
        self,
        model_name: str = "BAAI/bge-small-en-v1.5",
        provider: Optional[str] = None,
        device: str = "cpu",
        normalize: bool = True
    ):
        # Resolve aliases
        self.model_name = self.MODEL_ALIASES.get(model_name.lower().strip(), model_name)
        self.provider = (provider or ("gemini" if "text-embedding" in self.model_name else "huggingface")).lower()
        self.device = device
        self.normalize = normalize
        self.model = None
        self.gemini_client = None
        self._is_e5 = "e5" in self.model_name.lower()
        self._is_bge = "bge" in self.model_name.lower()
        self._is_gemini = self.provider == "gemini" or "text-embedding" in self.model_name

        self._init_model()

    def _init_model(self):
        if self._is_gemini:
            # Google Gemini Embeddings API (Zero download, Cloud-based)
            api_key = os.getenv("GEMINI_API_KEY")
            if api_key:
                try:
                    import google.generativeai as genai
                    genai.configure(api_key=api_key)
                    self.gemini_client = genai
                    logger.info(f"Initialized Google Gemini Embeddings API: '{self.model_name}' (Zero Local Download)")
                    return
                except ImportError:
                    logger.warning("google.generativeai not installed for Gemini embeddings.")
            else:
                logger.warning("GEMINI_API_KEY not found for Gemini embeddings.")

        # Local HuggingFace SentenceTransformers
        try:
            try:
                import torch
                torch.set_num_threads(1)
                torch.set_grad_enabled(False)
            except Exception:
                pass

            from sentence_transformers import SentenceTransformer
            logger.info(f"Loading Local Model: '{self.model_name}' on device '{self.device}'...")
            try:
                self.model = SentenceTransformer(self.model_name, device=self.device, local_files_only=True)
            except Exception:
                self.model = SentenceTransformer(self.model_name, device=self.device)
            dim = getattr(self.model, "get_embedding_dimension", getattr(self.model, "get_sentence_embedding_dimension", lambda: 384))()
            logger.success(f"Model '{self.model_name}' loaded successfully (dim={dim})")

        except ImportError:
            logger.warning("sentence-transformers not installed. Using local deterministic fallback.")
        except Exception as e:
            logger.error(f"Error loading '{self.model_name}': {e}. Falling back to BGE small.")
            try:
                from sentence_transformers import SentenceTransformer
                self.model_name = "BAAI/bge-small-en-v1.5"
                self.model = SentenceTransformer(self.model_name, device=self.device, local_files_only=True)
            except Exception:
                pass


    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """Embeds a batch of texts/passages."""
        if self._is_gemini and self.gemini_client:
            try:
                # Gemini embedding API
                response = self.gemini_client.embed_content(
                    model=self.model_name,
                    content=texts,
                    task_type="retrieval_document"
                )
                return response["embedding"]
            except Exception as e:
                logger.error(f"Gemini API Embedding Error: {e}, falling back to local embeddings...")

        if self.model:
            if self._is_e5:
                formatted_texts = [f"passage: {t}" if not t.startswith("passage:") else t for t in texts]
            else:
                formatted_texts = texts

            import torch
            with torch.no_grad():
                embeddings = self.model.encode(
                    formatted_texts,
                    batch_size=32,
                    normalize_embeddings=self.normalize,
                    show_progress_bar=False,
                    convert_to_numpy=True
                )
            result = embeddings.tolist()
            del embeddings
            return result
        else:
            return [[(hash(t + str(i)) % 1000) / 1000.0 for i in range(384)] for t in texts]


    def embed_query(self, query: str) -> List[float]:
        """Embeds a single search query."""
        if self._is_gemini and self.gemini_client:
            try:
                response = self.gemini_client.embed_content(
                    model=self.model_name,
                    content=query,
                    task_type="retrieval_query"
                )
                return response["embedding"]
            except Exception as e:
                logger.error(f"Gemini API Query Embedding Error: {e}")

        if self.model:
            if self._is_e5:
                formatted_query = f"query: {query}" if not query.startswith("query:") else query
            elif self._is_bge:
                formatted_query = f"Represent this sentence for searching relevant passages: {query}"
            else:
                formatted_query = query

            emb = self.model.encode(formatted_query, normalize_embeddings=self.normalize, convert_to_numpy=True)
            return emb.tolist()
        else:
            return [(hash(query + str(i)) % 1000) / 1000.0 for i in range(384)]

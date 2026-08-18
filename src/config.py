import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class PathConfig(BaseModel):
    raw_pdfs_dir: str = "./data/raw_pdfs"
    processed_dir: str = "./data/processed"
    knowledge_base_dir: str = "./data/knowledge_base"
    vector_db_dir: str = "./data/vector_db"
    eval_datasets_dir: str = "./eval_datasets"
    output_reports_dir: str = "./reports"

class IngestionConfig(BaseModel):
    chunking_strategy: str = "section_aware"
    chunk_size: int = 600
    chunk_overlap: int = 100
    min_chunk_length: int = 50
    preserve_section_headers: bool = True
    extract_tables: bool = True
    extract_images_metadata: bool = False

class EmbeddingsConfig(BaseModel):
    provider: str = Field(default_factory=lambda: os.getenv("EMBEDDING_PROVIDER", "gemini" if os.getenv("GEMINI_API_KEY") else "huggingface"))
    model_name: str = Field(default_factory=lambda: os.getenv("EMBEDDING_MODEL", "models/text-embedding-004" if os.getenv("GEMINI_API_KEY") else "BAAI/bge-small-en-v1.5"))
    device: str = "cpu"
    normalize_embeddings: bool = True
    batch_size: int = 32

class VectorStoreConfig(BaseModel):
    type: str = "chromadb"
    collection_name: str = "vera_clinical_guidelines"
    distance_metric: str = "cosine"

class RetrievalConfig(BaseModel):
    top_k: int = 4
    search_type: str = "hybrid"
    similarity_threshold: float = 0.60
    bm25_weight: float = 0.3
    dense_weight: float = 0.7
    rerank_enabled: bool = False
    reranker_model: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"

class GenerationConfig(BaseModel):
    provider: str = "openai"
    model_name: str = "gpt-4o-mini"
    temperature: float = 0.0
    max_tokens: int = 1024
    strict_grounding: bool = True

class SafetyConfig(BaseModel):
    confidence_gate_enabled: bool = True
    min_retrieval_confidence: float = 0.62
    hallucination_check_enabled: bool = True
    nli_threshold: float = 0.75
    enable_medical_disclaimer: bool = True
    disclaimer_text: str = "VERA is an evidence-grounded research assistant and does not provide autonomous clinical diagnosis or replace medical practitioners."

class EvaluationConfig(BaseModel):
    metrics: list = ["precision_at_k", "recall_at_k", "citation_accuracy", "faithfulness", "answer_relevance"]
    benchmark_file: str = "./eval_datasets/gold_ground_truth_qa.json"

class TelegramConfig(BaseModel):
    bot_token: Optional[str] = Field(default_factory=lambda: os.getenv("TELEGRAM_BOT_TOKEN", ""))
    webhook_url: Optional[str] = Field(default_factory=lambda: os.getenv("TELEGRAM_WEBHOOK_URL", ""))
    webhook_secret: Optional[str] = Field(default_factory=lambda: os.getenv("TELEGRAM_WEBHOOK_SECRET", ""))


class AppConfig(BaseModel):
    paths: PathConfig = Field(default_factory=PathConfig)
    ingestion: IngestionConfig = Field(default_factory=IngestionConfig)
    embeddings: EmbeddingsConfig = Field(default_factory=EmbeddingsConfig)
    vector_store: VectorStoreConfig = Field(default_factory=VectorStoreConfig)
    retrieval: RetrievalConfig = Field(default_factory=RetrievalConfig)
    generation: GenerationConfig = Field(default_factory=GenerationConfig)
    safety: SafetyConfig = Field(default_factory=SafetyConfig)
    evaluation: EvaluationConfig = Field(default_factory=EvaluationConfig)
    telegram: TelegramConfig = Field(default_factory=TelegramConfig)


def load_config(config_path: str = "config/config.yaml") -> AppConfig:
    """Load configuration from YAML file and merge with environment overrides."""
    config_file = Path(config_path)
    if config_file.exists():
        with open(config_file, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
            return AppConfig(**data)
    return AppConfig()

# Global default config instance
CONFIG = load_config()

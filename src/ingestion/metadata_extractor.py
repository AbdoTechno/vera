from typing import Dict, Any, List
from pathlib import Path

class MetadataExtractor:
    """Standardizes document metadata for clinical compliance and citation accuracy."""

    @staticmethod
    def extract_document_meta(file_path: str, custom_registry: Dict[str, Any] = None) -> Dict[str, Any]:
        path = Path(file_path)
        filename = path.name
        
        if custom_registry and filename in custom_registry:
            return custom_registry[filename]

        return {
            "doc_id": path.stem,
            "filename": filename,
            "title": path.stem.replace("_", " "),
            "category": "Clinical Practice Guideline",
            "source": "Medical Repository"
        }

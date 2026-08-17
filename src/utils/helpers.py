import json
import re
from pathlib import Path
from typing import Any, Dict, List, Union

def clean_text(text: str) -> str:
    """Removes excessive whitespaces, hyphens across linebreaks, and non-printable characters."""
    if not text:
        return ""
    # Fix hyphenated line-breaks (e.g. treat-\nment -> treatment)
    text = re.sub(r'(\w+)-\n(\w+)', r'\1\2', text)
    # Replace multiple spaces/newlines with single space
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def format_citation_string(doc_name: str, section: str, page_number: Union[int, str]) -> str:
    """Formats standardized clinical citation."""
    return f"[{doc_name} | Section: {section} | Page: {page_number}]"

def save_json(data: Any, file_path: Union[str, Path]) -> None:
    """Saves data as formatted JSON with UTF-8 encoding."""
    path = Path(file_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def load_json(file_path: Union[str, Path]) -> Any:
    """Loads data from JSON file."""
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)

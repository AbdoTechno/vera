import json
from pathlib import Path

registry_path = Path(r"d:\AI Hackathon\New data\data\processed\document_registry.json")
catalog_path = Path(r"d:\AI Hackathon\New data\data\processed\chunk_catalog.json")

# 1. Clean Registry
with open(registry_path, "r", encoding="utf-8") as f:
    registry = json.load(f)

unique_docs = {}
cleaned_registry = []

for doc in registry:
    fn = doc.get("filename", "").strip()
    if fn and fn.lower() not in unique_docs:
        unique_docs[fn.lower()] = doc
        cleaned_registry.append(doc)

# Re-assign sequential IDs DOC_001, DOC_002...
for idx, doc in enumerate(cleaned_registry, start=1):
    doc["doc_id"] = f"DOC_{idx:03d}"

with open(registry_path, "w", encoding="utf-8") as f:
    json.dump(cleaned_registry, f, indent=2, ensure_ascii=False)

print(f"Cleaned registry: reduced from {len(registry)} to {len(cleaned_registry)} unique documents.")

# 2. Clean Chunk Catalog
with open(catalog_path, "r", encoding="utf-8") as f:
    catalog = json.load(f)

# Map filename to canonical doc_id
fn_to_doc_id = {d["filename"]: d["doc_id"] for d in cleaned_registry}

seen_chunks = set()
cleaned_catalog = []

for chunk in catalog:
    fn = chunk.get("doc_name", "")
    page = chunk.get("page_number", 1)
    content_snippet = chunk.get("content", "")[:100]
    
    # Key for deduplication
    key = (fn.lower(), page, content_snippet)
    if key not in seen_chunks:
        seen_chunks.add(key)
        # update doc_id to match canonical registry
        if fn in fn_to_doc_id:
            chunk["doc_id"] = fn_to_doc_id[fn]
        cleaned_catalog.append(chunk)

with open(catalog_path, "w", encoding="utf-8") as f:
    json.dump(cleaned_catalog, f, indent=2, ensure_ascii=False)

print(f"Cleaned catalog: reduced from {len(catalog)} to {len(cleaned_catalog)} unique chunks.")

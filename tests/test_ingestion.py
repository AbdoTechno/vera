import pytest
from src.ingestion.chunker import MedicalChunker, Chunk

def test_section_aware_chunker():
    chunker = MedicalChunker(chunk_size=100, chunk_overlap=20, min_chunk_length=5)

    
    mock_pages = [
        {
            "doc_name": "TestGuideline.pdf",
            "page_number": 1,
            "text": "INTRODUCTION\nSpinal muscular atrophy is an autosomal recessive neuromuscular disease.\nTREATMENT RECOMMENDATIONS\nNusinersen should be initiated as early as possible.",
            "metadata": {"doc_id": "DOC_TEST"}
        }
    ]
    
    chunks = chunker.chunk_pages(mock_pages)
    assert len(chunks) >= 1
    assert chunks[0].doc_name == "TestGuideline.pdf"
    assert chunks[0].page_number == 1

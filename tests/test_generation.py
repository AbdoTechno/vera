import pytest
from src.generation.citation_formatter import CitationFormatter

def test_citation_extraction():
    text = "Treatment should start immediately [ClinPediatr_2023.pdf | Section: Treatment | Page: 4]."
    citations = CitationFormatter.extract_citations(text)
    
    assert len(citations) == 1
    assert citations[0]["doc_name"] == "ClinPediatr_2023.pdf"
    assert citations[0]["section"] == "Treatment"
    assert citations[0]["page"] == "4"

import pytest
from src.retrieval.query_expansion import MedicalQueryExpander

def test_query_expansion():
    expander = MedicalQueryExpander()
    query = "What is the recommended dose of Spinraza for SMA?"
    expanded = expander.expand(query)
    
    assert "nusinersen" in expanded.lower() or "spinal muscular atrophy" in expanded.lower()

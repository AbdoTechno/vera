import pytest
from src.safety.refusal_engine import RefusalEngine
from src.safety.confidence_gate import ConfidenceGate

def test_emergency_refusal():
    emergency_query = "Patient has severe bleeding and cardiac arrest!"
    res = RefusalEngine.check_pre_retrieval_refusal(emergency_query)
    
    assert res is not None
    assert res["is_refusal"] is True
    assert res["reason"] == "EMERGENCY_ALERT"

def test_out_of_scope_refusal():
    out_of_scope_query = "What is the insulin treatment plan for diabetes?"
    res = RefusalEngine.check_pre_retrieval_refusal(out_of_scope_query)
    
    assert res is not None
    assert res["is_refusal"] is True
    assert res["reason"] == "OUT_OF_SCOPE_QUERY"

def test_confidence_gate_rejection():
    gate = ConfidenceGate(min_confidence=0.70)
    low_confidence_chunks = [
        {"content": "random text", "similarity_score": 0.45}
    ]
    eval_result = gate.evaluate(low_confidence_chunks)
    assert eval_result["passed"] is False

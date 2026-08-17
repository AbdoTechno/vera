import pytest
import html
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi.testclient import TestClient
from src.api.main import app
from src.api.telegram_service import TelegramService
from src.utils.telegram_formatter import (
    escape_html,
    split_telegram_message,
    format_clinical_response_for_telegram,
    get_welcome_message,
    get_help_message,
    get_error_message
)
from src.api.schemas import (
    ChatResponse, ClinicalResponse, CitationItem, DoctorContext, MedicalDomains,
    RAGPipelineSimulation, Step1QueryAnalysis, Step2Retrieval, Step3Safety, Step4Synthesis
)

client = TestClient(app)

# Helper mock factory for ChatResponse
def create_mock_chat_response(summary="Test summary", recs=None, citations=None, score=0.85):
    recs = recs or ["Recommendation 1", "Recommendation 2"]
    citations = citations or [CitationItem(citation_id=1, source="guideline.pdf", page=4, section="Dosing", doclink="guideline.pdf#page=4")]
    
    sim = RAGPipelineSimulation(
        step_1_query_analysis=Step1QueryAnalysis(original_query="q", disease_category="SMA", intent="Dosing"),
        step_2_retrieval=Step2Retrieval(search_type="Hybrid", retrieved_count=1, sources_found=[]),
        step_3_safety_and_verification=Step3Safety(confidence_score=score, passed_safety_gate=True, hallucination_check="Pass", status="Safe"),
        step_4_synthesis=Step4Synthesis(model_used="Gemini", latency_seconds=1.5, status="Generated")
    )
    
    return ChatResponse(
        status="success",
        language="en",
        doctor_context=DoctorContext(name="Dr. Test"),
        rag_pipeline_simulation=sim,
        clinical_response=ClinicalResponse(
            summary=summary,
            detailed_recommendations=recs,
            citations=citations,
            medical_disclaimer="VERA is a research assistant.",
            confidence_score=score,
            confidence_percentage=f"{int(score*100)}%"
        ),
        available_medical_domains=MedicalDomains(
            active=["SMA Guidelines"],
            upcoming_soon=["Pediatric Oncology"]
        )
    )


# 1. Test Telegram Formatter
def test_escape_html():
    assert escape_html("<b>hello</b> & 'world'") == "&lt;b&gt;hello&lt;/b&gt; &amp; &#x27;world&#x27;"
    assert escape_html("") == ""

def test_format_clinical_response():
    mock_resp = create_mock_chat_response()
    formatted = format_clinical_response_for_telegram(mock_resp)
    
    assert "<b>VERA CLINICAL DECISION SUPPORT</b>" in formatted
    assert "<code>Confidence: 85% | Verified Evidence</code>" in formatted
    assert "📋 <b>EXECUTIVE SUMMARY</b>" in formatted
    assert "<blockquote>Test summary</blockquote>" in formatted
    assert "💡 <b>KEY CLINICAL RECOMMENDATIONS</b>" in formatted
    assert "<b>1.</b> Recommendation 1" in formatted
    assert "📚 <b>VERIFIED EVIDENCE SOURCES</b>" in formatted
    assert "<b>[1]</b> <code>guideline.pdf</code>" in formatted
    assert "⚖️ <i>Disclaimer: VERA is a research assistant.</i>" in formatted



def test_split_telegram_message_short():
    text = "Short clinical message."
    chunks = split_telegram_message(text, max_length=100)
    assert len(chunks) == 1
    assert chunks[0] == text

def test_split_telegram_message_long_paragraphs():
    p1 = "A" * 200
    p2 = "B" * 200
    full = f"{p1}\n\n{p2}"
    chunks = split_telegram_message(full, max_length=250)
    assert len(chunks) == 2
    assert chunks[0] == p1
    assert chunks[1] == p2

# 2. Test Telegram Service Commands & Processing
@pytest.mark.asyncio
async def test_telegram_service_start_command():
    svc = TelegramService(bot_token="123456:ABC-DEF")
    mock_rag = MagicMock()
    
    with patch.object(svc, "send_message", new_callable=AsyncMock) as mock_send:
        mock_send.return_value = True
        update = {
            "message": {
                "chat": {"id": 999},
                "from": {"first_name": "Doctor Sarah"},
                "text": "/start"
            }
        }
        res = await svc.process_update(update, mock_rag)
        assert res["status"] == "handled"
        assert res["action"] == "start"
        mock_send.assert_called_once()
        args, _ = mock_send.call_args
        assert args[0] == 999
        assert "Welcome to VERA" in args[1]

@pytest.mark.asyncio
async def test_telegram_service_help_command():
    svc = TelegramService(bot_token="123456:ABC-DEF")
    mock_rag = MagicMock()
    
    with patch.object(svc, "send_message", new_callable=AsyncMock) as mock_send:
        mock_send.return_value = True
        update = {
            "message": {
                "chat": {"id": 999},
                "from": {"first_name": "Doctor"},
                "text": "/help"
            }
        }
        res = await svc.process_update(update, mock_rag)
        assert res["status"] == "handled"
        assert res["action"] == "help"
        mock_send.assert_called_once()
        args, _ = mock_send.call_args
        assert "VERA Usage Guide" in args[1]

@pytest.mark.asyncio
async def test_telegram_service_clinical_query_success():
    svc = TelegramService(bot_token="123456:ABC-DEF")
    mock_rag = MagicMock()
    mock_rag.process_clinical_query.return_value = create_mock_chat_response(
        summary="Nusinersen dosing is 12 mg per administration."
    )
    
    with patch.object(svc, "send_message", new_callable=AsyncMock) as mock_send, \
         patch.object(svc, "send_chat_action", new_callable=AsyncMock) as mock_action:
        mock_send.return_value = True
        mock_action.return_value = True
        
        update = {
            "message": {
                "chat": {"id": 999},
                "from": {"first_name": "Dr. Sarah", "username": "drsarah"},
                "text": "What is the recommended dosing for Nusinersen?"
            }
        }
        res = await svc.process_update(update, mock_rag)
        assert res["status"] == "success"
        mock_action.assert_called_once_with(999, "typing")
        mock_send.assert_called_once()
        args, _ = mock_send.call_args
        assert "Nusinersen dosing is 12 mg" in args[1]
        assert "guideline.pdf" in args[1]

@pytest.mark.asyncio
async def test_telegram_service_non_text_message():
    svc = TelegramService(bot_token="123456:ABC-DEF")
    mock_rag = MagicMock()
    
    with patch.object(svc, "send_message", new_callable=AsyncMock) as mock_send:
        mock_send.return_value = True
        update = {
            "message": {
                "chat": {"id": 999},
                "from": {"first_name": "Doctor"},
                "photo": [{"file_id": "123"}]  # No text
            }
        }
        res = await svc.process_update(update, mock_rag)
        assert res["status"] == "handled"
        assert res["reason"] == "non_text_message"
        mock_send.assert_called_once()

@pytest.mark.asyncio
async def test_telegram_service_rag_failure_fallback():
    svc = TelegramService(bot_token="123456:ABC-DEF")
    mock_rag = MagicMock()
    mock_rag.process_clinical_query.side_effect = RuntimeError("Database timeout")
    
    with patch.object(svc, "send_message", new_callable=AsyncMock) as mock_send, \
         patch.object(svc, "send_chat_action", new_callable=AsyncMock):
        mock_send.return_value = True
        
        update = {
            "message": {
                "chat": {"id": 999},
                "from": {"first_name": "Doctor"},
                "text": "Clinical query triggering error"
            }
        }
        res = await svc.process_update(update, mock_rag)
        assert res["status"] == "error"
        mock_send.assert_called_once()
        args, _ = mock_send.call_args
        assert "could not process your clinical request" in args[1]

# 3. Test FastAPI Webhook Endpoints
def test_telegram_webhook_endpoint_success():
    update_payload = {
        "message": {
            "chat": {"id": 12345},
            "from": {"first_name": "Tester"},
            "text": "What are SMA treatments?"
        }
    }
    response = client.post("/telegram/webhook", json=update_payload)
    assert response.status_code == 200
    data = response.json()
    assert data["ok"] is True
    assert data["status"] == "processing"

def test_telegram_webhook_secret_validation():
    with patch("src.config.CONFIG.telegram.webhook_secret", "my-secret-key"):
        # Without header -> 403
        resp1 = client.post("/telegram/webhook", json={"message": {"text": "hello"}})
        assert resp1.status_code == 403

        # With correct header -> 200
        resp2 = client.post(
            "/telegram/webhook",
            json={"message": {"text": "hello"}},
            headers={"X-Telegram-Bot-Api-Secret-Token": "my-secret-key"}
        )
        assert resp2.status_code == 200

def test_set_webhook_missing_url():
    with patch("src.config.CONFIG.telegram.webhook_url", ""):
        resp = client.post("/telegram/set-webhook", json={})
        assert resp.status_code == 400
        assert "Webhook URL not provided" in resp.json()["detail"]

def test_set_webhook_non_https():
    resp = client.post("/telegram/set-webhook", json={"webhook_url": "http://insecure.domain.com/webhook"})
    assert resp.status_code == 400
    assert "HTTPS" in resp.json()["detail"]

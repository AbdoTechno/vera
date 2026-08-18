"""
VERA Clinical Intelligence Platform - Hugging Face Spaces Entrypoint
Runs FastAPI backend seamlessly on Hugging Face Gradio Free Tier.
"""

import os
import gradio as gr
from src.api.main import app as fastapi_app

# Create a clean monitoring landing UI for Gradio while exposing full FastAPI endpoints
with gr.Blocks(title="VERA Clinical Intelligence Platform") as demo:
    gr.Markdown("# 🩺 VERA Clinical Intelligence Platform")
    gr.Markdown("""
    ### Evidence-Grounded Clinical Decision Support RAG Backend
    
    The FastAPI backend is running live and ready for API requests from Flutter and web clients.
    
    - 📖 **Interactive Swagger API Docs:** [/docs](/docs)
    - 🩺 **Health Check:** [/api/v1/health](/api/v1/health)
    - 📄 **Indexed Medical Guidelines:** [/api/v1/documents](/api/v1/documents)
    - 💬 **Clinical RAG Chat Endpoint:** `POST /api/v1/chat`
    - 🛡️ **Document Ingestion Guardrail:** `POST /api/v1/upload-document`
    """)

# Mount FastAPI app onto Gradio
app = gr.mount_gradio_app(fastapi_app, demo, path="/")

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 7860))
    uvicorn.run(app, host="0.0.0.0", port=port)

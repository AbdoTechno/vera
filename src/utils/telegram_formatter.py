import html
import re
from typing import List, Optional
from src.api.schemas import ChatResponse, ClinicalResponse

def escape_html(text: str) -> str:
    """Escapes HTML special characters for safe Telegram HTML parse mode."""
    if not text:
        return ""
    return html.escape(str(text))

def format_clinical_response_for_telegram(chat_resp: ChatResponse) -> str:
    """Formats a full VERA ChatResponse into a highlighted, professional Telegram HTML message."""
    c_resp: ClinicalResponse = chat_resp.clinical_response
    
    parts: List[str] = []
    
    # 1. Header & Confidence Badge
    conf_str = escape_html(c_resp.confidence_percentage or "85%")
    parts.append(f"🩺 <b>VERA CLINICAL DECISION SUPPORT</b>\n<code>Confidence: {conf_str} | Verified Evidence</code>\n")
    
    # 2. Executive Summary (Rendered inside Telegram Blockquote)
    if c_resp.summary:
        summary_escaped = escape_html(c_resp.summary)
        parts.append(f"📋 <b>EXECUTIVE SUMMARY</b>\n<blockquote>{summary_escaped}</blockquote>\n")
        
    # 3. Clinical Recommendations with distinct bullet styling
    if c_resp.detailed_recommendations:
        recs_text = []
        for i, rec in enumerate(c_resp.detailed_recommendations, 1):
            clean_rec = rec.strip()
            # If the recommendation has a title prefix (e.g. "Dosing Protocol: ...")
            if ":" in clean_rec:
                title_part, rest_part = clean_rec.split(":", 1)
                rest_escaped = escape_html(rest_part.strip())
                # Highlight in-line bracket citations with monospace code badge
                rest_escaped = re.sub(r'\[([^\]]+)\]', r'<code>[\1]</code>', rest_escaped)
                recs_text.append(f"<b>{i}. {escape_html(title_part.strip())}:</b>\n   {rest_escaped}\n")
            else:
                escaped = escape_html(clean_rec)
                escaped = re.sub(r'\[([^\]]+)\]', r'<code>[\1]</code>', escaped)
                recs_text.append(f"<b>{i}.</b> {escaped}\n")
                
        parts.append("💡 <b>KEY CLINICAL RECOMMENDATIONS</b>\n" + "\n".join(recs_text))
        
    # 4. Citations & Evidence Sources
    if c_resp.citations:
        cite_text = []
        for c in c_resp.citations:
            source_name = escape_html(c.source)
            page_info = f"Page {c.page}" if c.page else "General"
            sec_info = f" — {escape_html(c.section)}" if c.section and c.section != "Clinical Protocols" else ""
            cite_text.append(f"• <b>[{c.citation_id}]</b> <i>{source_name}</i> (<code>{page_info}</code>{sec_info})")
        parts.append("📚 <b>VERIFIED EVIDENCE SOURCES</b>\n" + "\n".join(cite_text) + "\n")
        
    # 5. Disclaimer
    if c_resp.medical_disclaimer:
        disclaimer_escaped = escape_html(c_resp.medical_disclaimer)
        parts.append(f"⚖️ <i>{disclaimer_escaped}</i>")
        
    return "\n".join(parts)


def split_telegram_message(text: str, max_length: int = 3800) -> List[str]:
    """Splits a long message safely into chunks within Telegram length limits (<= 4096).
    
    Prefers splitting at paragraph boundaries (double newlines), then newlines, then spaces.
    """
    if not text:
        return [""]
        
    if len(text) <= max_length:
        return [text]
        
    chunks: List[str] = []
    current_chunk = ""
    
    # Split into paragraphs first
    paragraphs = text.split("\n\n")
    
    for para in paragraphs:
        if not para.strip():
            continue
            
        # If adding this paragraph fits, add it
        if len(current_chunk) + len(para) + 2 <= max_length:
            if current_chunk:
                current_chunk += "\n\n" + para
            else:
                current_chunk = para
        else:
            # Current chunk is full, push it
            if current_chunk:
                chunks.append(current_chunk)
                current_chunk = ""
                
            # If paragraph itself is larger than max_length, split by lines
            if len(para) > max_length:
                lines = para.split("\n")
                for line in lines:
                    if len(current_chunk) + len(line) + 1 <= max_length:
                        if current_chunk:
                            current_chunk += "\n" + line
                        else:
                            current_chunk = line
                    else:
                        if current_chunk:
                            chunks.append(current_chunk)
                            current_chunk = ""
                        # If a single line is still too large, split by words
                        if len(line) > max_length:
                            words = line.split(" ")
                            for word in words:
                                if len(current_chunk) + len(word) + 1 <= max_length:
                                    if current_chunk:
                                        current_chunk += " " + word
                                    else:
                                        current_chunk = word
                                else:
                                    if current_chunk:
                                        chunks.append(current_chunk)
                                    current_chunk = word
                        else:
                            current_chunk = line
            else:
                current_chunk = para
                
    if current_chunk:
        chunks.append(current_chunk)
        
    return chunks

def get_welcome_message() -> str:
    """Returns the welcome greeting for /start."""
    return (
        "<b>Welcome to VERA (Verified Evidence Retrieval Assistant)</b>\n\n"
        "I am an evidence-grounded Clinical Decision Support assistant designed for physicians, geneticists, and medical researchers.\n\n"
        "<b>How to use VERA:</b>\n"
        "• Send any clinical or genetic inquiry (e.g., treatment protocols, dosing, diagnostic criteria, genetic variants).\n"
        "• All answers are strictly synthesized from peer-reviewed guidelines with exact page citations.\n\n"
        "Type /help for usage guidance and sample questions."
    )

def get_help_message() -> str:
    """Returns the usage instructions for /help."""
    return (
        "<b>VERA Usage Guide</b>\n\n"
        "<b>Available Commands:</b>\n"
        "/start - Welcome overview\n"
        "/help - Instructions and sample queries\n\n"
        "<b>Sample Clinical Questions:</b>\n"
        "• <i>What are the initiation criteria and dosing considerations for Nusinersen in SMA patients?</i>\n"
        "• <i>How do long-read sequencing technologies resolve complex chromosomal rearrangements?</i>\n"
        "• <i>What are the monitoring requirements during SMN-modifying therapy?</i>\n\n"
        "<i>Note: VERA is a decision-support and research assistant and does not replace autonomous clinical diagnosis.</i>"
    )

def get_error_message() -> str:
    """Returns a safe, professional fallback message on internal failure."""
    return (
        "<b>Notice:</b> VERA could not process your clinical request at this moment. "
        "Please rephrase your inquiry or try again shortly."
    )

import os
import httpx
from typing import Dict, Any, Optional, List
from src.config import CONFIG
from src.api.schemas import ChatRequest, ChatResponse, DoctorContext
from src.api.service import VERAClinicalService
import json
from pathlib import Path
from src.utils.telegram_formatter import (
    format_clinical_response_for_telegram,
    split_telegram_message,
    get_welcome_message,
    get_help_message,
    get_error_message
)
from src.utils.logger import logger

class TelegramService:
    """Service handling Telegram Bot API communication, per-user BYOK keys, and VERA RAG dispatch."""

    def __init__(self, bot_token: Optional[str] = None):
        self.bot_token = bot_token or CONFIG.telegram.bot_token or os.getenv("TELEGRAM_BOT_TOKEN", "")
        self.base_url = f"https://api.telegram.org/bot{self.bot_token}" if self.bot_token else ""
        self.keys_file = Path("./data/telegram_user_keys.json")
        self.user_keys: Dict[str, str] = self._load_user_keys()

    def _load_user_keys(self) -> Dict[str, str]:
        """Loads persistent per-user Telegram Gemini API keys."""
        if self.keys_file.exists():
            try:
                with open(self.keys_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading telegram_user_keys: {e}")
        return {}

    def _save_user_keys(self):
        """Persists per-user Telegram keys to disk."""
        try:
            self.keys_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.keys_file, "w", encoding="utf-8") as f:
                json.dump(self.user_keys, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving telegram_user_keys: {e}")

    def get_user_key(self, chat_id: int | str) -> Optional[str]:
        """Gets API key configured specifically by this Telegram user."""
        return self.user_keys.get(str(chat_id))

    def _mask_token(self, text: str) -> str:
        """Sanitizes text to prevent accidental token exposure in logs."""
        if not self.bot_token:
            return text
        return text.replace(self.bot_token, "[REDACTED_TELEGRAM_TOKEN]")

    async def send_chat_action(self, chat_id: int | str, action: str = "typing") -> bool:
        """Sends a chat action (e.g. typing) to indicate background processing."""
        if not self.bot_token:
            logger.warning("Telegram Bot Token is not configured. Cannot send chat action.")
            return False

        url = f"{self.base_url}/sendChatAction"
        payload = {"chat_id": chat_id, "action": action}

        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                resp = await client.post(url, json=payload)
                return resp.status_code == 200
        except Exception as e:
            logger.debug(f"Could not send chat action: {self._mask_token(str(e))}")
            return False

    async def send_message(
        self,
        chat_id: int | str,
        text: str,
        parse_mode: str = "HTML"
    ) -> bool:
        """Sends one or multiple messages to a Telegram chat, safely splitting if exceeding length limits."""
        if not self.bot_token:
            logger.warning("Telegram Bot Token is not configured. Cannot send message.")
            return False

        chunks = split_telegram_message(text, max_length=3800)
        url = f"{self.base_url}/sendMessage"
        all_success = True

        async with httpx.AsyncClient(timeout=15.0) as client:
            for chunk in chunks:
                payload = {
                    "chat_id": chat_id,
                    "text": chunk,
                    "parse_mode": parse_mode
                }
                try:
                    resp = await client.post(url, json=payload)
                    
                    # If HTML parsing failed due to unexpected tag, retry as plain text
                    if resp.status_code != 200 and parse_mode == "HTML":
                        logger.warning(f"Telegram HTML send failed ({resp.status_code}), retrying without parse_mode.")
                        payload["parse_mode"] = None
                        resp = await client.post(url, json=payload)

                    if resp.status_code != 200:
                        all_success = False
                        logger.error(f"Telegram API send error: status={resp.status_code}, response={self._mask_token(resp.text)}")
                except Exception as e:
                    all_success = False
                    logger.error(f"Telegram network error: {self._mask_token(str(e))}")

        return all_success

    async def set_webhook(self, webhook_url: str, secret_token: Optional[str] = None) -> Dict[str, Any]:
        """Registers the FastAPI webhook endpoint with Telegram."""
        if not self.bot_token:
            return {"ok": False, "description": "TELEGRAM_BOT_TOKEN is not set."}

        url = f"{self.base_url}/setWebhook"
        payload: Dict[str, Any] = {"url": webhook_url}
        if secret_token:
            payload["secret_token"] = secret_token

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.post(url, json=payload)
                data = resp.json()
                logger.info(f"Telegram setWebhook result: {data.get('description', 'Done')}")
                return data
        except Exception as e:
            masked_err = self._mask_token(str(e))
            logger.error(f"Failed to set webhook: {masked_err}")
            return {"ok": False, "description": masked_err}

    async def remove_webhook(self) -> Dict[str, Any]:
        """Deletes the current Telegram webhook."""
        if not self.bot_token:
            return {"ok": False, "description": "TELEGRAM_BOT_TOKEN is not set."}

        url = f"{self.base_url}/deleteWebhook"
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.post(url)
                return resp.json()
        except Exception as e:
            masked_err = self._mask_token(str(e))
            logger.error(f"Failed to delete webhook: {masked_err}")
            return {"ok": False, "description": masked_err}

    async def get_webhook_info(self) -> Dict[str, Any]:
        """Queries Telegram for the current webhook status."""
        if not self.bot_token:
            return {"ok": False, "description": "TELEGRAM_BOT_TOKEN is not set."}

        url = f"{self.base_url}/getWebhookInfo"
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.get(url)
                return resp.json()
        except Exception as e:
            masked_err = self._mask_token(str(e))
            logger.error(f"Failed to get webhook info: {masked_err}")
            return {"ok": False, "description": masked_err}

    async def process_update(
        self,
        update_data: Dict[str, Any],
        rag_service: VERAClinicalService
    ) -> Dict[str, Any]:
        """Processes an incoming Telegram webhook update and dispatches to VERA RAG service with user BYOK."""
        message = update_data.get("message")
        if not message:
            return {"status": "ignored", "reason": "non_message_update"}

        chat = message.get("chat", {})
        chat_id = chat.get("id")
        if not chat_id:
            return {"status": "ignored", "reason": "missing_chat_id"}

        str_chat_id = str(chat_id)
        text = message.get("text", "").strip()
        if not text:
            await self.send_message(
                chat_id,
                "VERA currently processes text-based clinical inquiries. Please type your medical or research question."
            )
            return {"status": "handled", "reason": "non_text_message"}

        user = message.get("from", {})
        username = user.get("username") or user.get("first_name", "Doctor")

        # 1. Handle Key Setup Commands: /setkey <KEY> or /key <KEY>
        if text.startswith("/setkey") or text.startswith("/key"):
            parts = text.split(maxsplit=1)
            if len(parts) > 1 and len(parts[1].strip()) >= 20:
                raw_key = parts[1].strip()
                self.user_keys[str_chat_id] = raw_key
                self._save_user_keys()
                masked = raw_key[:6] + "..." + raw_key[-4:]
                await self.send_message(
                    chat_id,
                    f"✅ <b>تم حفظ وتفعيل مفتاح Gemini بنجاح!</b> 🩺\n\n"
                    f"🔑 <b>المفتاح المفعل:</b> <code>{masked}</code>\n\n"
                    f"يمكنك الآن طرح أي استفسار طبي وسريري مباشرة وسيقوم VERA بالرد مع التوثيق الكامل من الإرشادات المعتمدة."
                )
                return {"status": "handled", "action": "key_saved"}
            else:
                await self.send_message(
                    chat_id,
                    "⚠️ <b>يرجى إدخال مفتاح Gemini صالح.</b>\n\n"
                    "📌 <b>طريقة الاستخدام:</b>\n"
                    "<code>/setkey YOUR_GEMINI_API_KEY</code>\n\n"
                    "💡 <i>يمكنك الحصول على مفتاحك مجاناً من Google AI Studio (aistudio.google.com).</i>"
                )
                return {"status": "handled", "action": "key_syntax_error"}

        # 2. Handle /mykey
        if text == "/mykey":
            existing_key = self.user_keys.get(str_chat_id)
            if existing_key:
                masked = existing_key[:6] + "..." + existing_key[-4:]
                await self.send_message(
                    chat_id,
                    f"🔑 <b>مفتاحك الحالي:</b> <code>{masked}</code>\n\n"
                    f"لتحديث المفتاح أرسل:\n<code>/setkey NEW_KEY</code>\n"
                    f"لحذف المفتاح أرسل:\n<code>/delkey</code>"
                )
            else:
                await self.send_message(
                    chat_id,
                    "ℹ️ لم تقم بإدخال مفتاح Gemini بعد.\n\n"
                    "أرسل المفتاح مباشرة أو اكتب:\n<code>/setkey YOUR_KEY</code>"
                )
            return {"status": "handled", "action": "mykey"}

        # 3. Handle /delkey
        if text == "/delkey" or text == "/removekey":
            if str_chat_id in self.user_keys:
                del self.user_keys[str_chat_id]
                self._save_user_keys()
                await self.send_message(chat_id, "🗑️ تم حذف مفتاح Gemini الخاص بك بنجاح.")
            else:
                await self.send_message(chat_id, "ℹ️ لا يوجد مفتاح محفوظ لحذفه.")
            return {"status": "handled", "action": "key_deleted"}

        # 4. Auto-detect if user directly sent an API key (e.g. starts with AIzaSy)
        if text.startswith("AIzaSy") and len(text) >= 30 and " " not in text:
            self.user_keys[str_chat_id] = text
            self._save_user_keys()
            masked = text[:6] + "..." + text[-4:]
            await self.send_message(
                chat_id,
                f"✅ <b>تم تفعيل مفتاح Gemini API Key بنجاح!</b> 🩺\n\n"
                f"🔑 <b>المفتاح:</b> <code>{masked}</code>\n\n"
                f"أهلاً بك يا دكتور {username}! يمكنك الآن إرسال أي سؤال سريري أو جيني مباشرة."
            )
            return {"status": "handled", "action": "key_auto_saved"}

        # 5. Handle /start and /help commands
        if text.startswith("/start"):
            welcome_msg = get_welcome_message()
            if not self.get_user_key(chat_id):
                welcome_msg += (
                    "\n\n🔑 <b>تفعيل البوت (API Key):</b>\n"
                    "للبدء، يرجى إرسال مفتاح <b>Gemini API Key</b> الخاص بك مباشرة في المحادثة أو كتابة:\n"
                    "<code>/setkey YOUR_GEMINI_KEY</code>\n\n"
                    "<i>(احصل على مفتاحك مجاناً من aistudio.google.com)</i>"
                )
            await self.send_message(chat_id, welcome_msg)
            return {"status": "handled", "action": "start"}

        if text.startswith("/help"):
            help_msg = get_help_message()
            help_msg += (
                "\n\n<b>إدارة المفاتيح:</b>\n"
                "/setkey &lt;KEY&gt; - حفظ أو تحديث مفتاح Gemini الخاص بك\n"
                "/mykey - عرض حالة المفتاح\n"
                "/delkey - حذف المفتاح"
            )
            await self.send_message(chat_id, help_msg)
            return {"status": "handled", "action": "help"}

        # 6. Check if user has an active Gemini key
        effective_user_key = self.get_user_key(chat_id)
        if not effective_user_key:
            await self.send_message(
                chat_id,
                "👋 <b>مرحباً دكتور!</b>\n\n"
                "🔑 <b>لتفعيل استفسارات VERA الطبية:</b>\n"
                "يرجى تزويد البوت بمفتاح Google Gemini API Key الخاص بك.\n\n"
                "📌 <b>طريقة التفعيل السريعة:</b>\n"
                "أرسل المفتاح مباشرة في المحادثة، أو اكتب:\n"
                "<code>/setkey AIzaSy...</code>\n\n"
                "💡 <i>المفتاح مجاني بالكامل ويمكنك استخراجه في ثوانٍ من <a href=\"https://aistudio.google.com/\">Google AI Studio</a>، ويتم حفظه بشكل خاص وآمن لك فقط.</i>"
            )
            return {"status": "handled", "action": "key_required_prompt"}

        # 7. Handle Clinical Inquiries via VERA RAG
        try:
            await self.send_chat_action(chat_id, "typing")

            chat_request = ChatRequest(
                query=text,
                language="ar" if any('\u0600' <= c <= '\u06FF' for c in text) else "en",
                api_key=effective_user_key,
                doctor_context=DoctorContext(
                    name=username,
                    specialty="Clinical User (Telegram)",
                    notes="Telegram Bot Inquiry"
                )
            )

            chat_response: ChatResponse = rag_service.process_clinical_query(chat_request)
            formatted_text = format_clinical_response_for_telegram(chat_response)
            await self.send_message(chat_id, formatted_text)
            return {"status": "success", "action": "query_answered"}

        except Exception as e:
            err_str = str(e)
            logger.error(f"Error processing Telegram clinical inquiry: {self._mask_token(err_str)}", exc_info=True)
            
            if any(k in err_str.lower() for k in ["api_key_invalid", "api key not valid", "permission_denied", "401"]):
                await self.send_message(
                    chat_id,
                    "⚠️ <b>مفتاح Gemini API Key الخاص بك غير صالح أو منتهي الصلاحية.</b>\n\n"
                    "يرجى إرسال مفتاح جديد باستخدام:\n"
                    "<code>/setkey YOUR_NEW_KEY</code>"
                )
                return {"status": "error", "error": "invalid_api_key"}
            
            error_msg = get_error_message()
            await self.send_message(chat_id, error_msg)
            return {"status": "error", "error": "internal_rag_error"}

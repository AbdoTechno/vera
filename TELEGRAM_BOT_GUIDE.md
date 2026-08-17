# VERA Telegram Bot — Quickstart & User Guide
## دليل تشغيل واستخدام بوت التيليجرام (@veramedicalbot)

هذا الدليل يوضح بالخطوات البسيطة والمباشرة كيفية تشغيل خادم VERA RAG وربطه ببوت التيليجرام **`@veramedicalbot`** لبدء إرسال الأسئلة الطبية وتلقي الإجابات المدعومة بالأدلة والمراجع فوراً.

---

## 📋 المتطلبات الأساسية (Prerequisites)

1. تثبيت الحزم المطلوبة:
   ```bash
   pip install -r requirements.txt
   ```
2. وجود مفتاح Gemini API وتوكن التيليجرام في ملف `.env`:
   ```ini
   GEMINI_API_KEY=your_gemini_api_key
   TELEGRAM_BOT_TOKEN=8932080168:AAE8ki9YyH4QXQmOPfsI9HSfmc7rLSP9wnM
   ```
3. أداة فتح نفق محلي (مثل **ngrok** أو **Cloudflare Tunnel**) لاستقبال رسائل التيليجرام على جهازك.

---

## 🚀 خطوات التشغيل خطوة بخطوة (Step-by-Step)

### الخطوة 1: تشغيل خادم FastAPI
افتح نافذة Terminal وشغل الخادم:
```powershell
python run_server.py
```
أو عبر uvicorn مباشرة:
```powershell
uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload
```
> ستظهر لك رسالة: `VERA RAG services pre-warmed and ready for instant queries.` على الرابط `http://localhost:8000`.

---

### الخطوة 2: إنشاء نفق HTTPS عام عبر ngrok
افتح نافذة Terminal ثانية وشغل الأمر:
```powershell
ngrok http 8000
```
ستظهر لك شاشة ngrok وفيها رابط HTTPS عام مثل:
```text
Forwarding   https://a1b2-c3d4.ngrok-free.app -> http://localhost:8000
```
> انسخ رابط الـ HTTPS هذا (مثال: `https://a1b2-c3d4.ngrok-free.app`).

---

### الخطوة 3: تفعيل الـ Webhook مع التيليجرام (بأمر واحد)
يمكنك تفعيل الـ Webhook بإحدى طريقتين:

#### الطريقة الأولى (عبر المتصفح - الأسهل):
1. افتح صفحة التوثيق التفاعلية: [http://localhost:8000/docs](http://localhost:8000/docs)
2. انزل إلى قسم **Telegram Bot Integration** ثم افتح `POST /telegram/set-webhook`.
3. اضغط **Try it out**، وضع في خانة `webhook_url` الرابط الخاص بك متبوعاً بـ `/telegram/webhook`:
   ```json
   {
     "webhook_url": "https://a1b2-c3d4.ngrok-free.app/telegram/webhook"
   }
   ```
4. اضغط **Execute** وستظهر لك النتيجة: `{"ok": true, "description": "Webhook was set"}`.

#### الطريقة الثانية (عبر التيرمينال - cURL):
```powershell
curl -X POST "http://localhost:8000/telegram/set-webhook" `
     -H "Content-Type: application/json" `
     -d '{\"webhook_url\": \"https://a1b2-c3d4.ngrok-free.app/telegram/webhook\"}'
```

---

### الخطوة 4: فتح التيليجرام وبدء الاستخدام 💬
1. افتح تطبيق Telegram على هاتفك أو جهازك.
2. ابحث عن اسم البوت: **`@veramedicalbot`** (أو افتح الرابط المباشر: `https://t.me/veramedicalbot`).
3. اضغط **Start** أو أرسل `/start` لتلقي الترحيب.
4. أرسل استفسارك الطبي باللغة الإنجليزية، مثل:
   > **"What are the approved therapies for Spinal Muscular Atrophy?"**
   
   > **"What is the recommended dosing and administration protocol for Nusinersen?"**
   
   > **"What baseline laboratory tests are required before initiating SMN2-targeting therapy?"**

5. سيقوم البوت بما يلي:
   - إظهار مؤشر الكتابة `typing...` أثناء البحث في الأدبيات الطبية.
   - استخراج وتوليد الإجابة المدعومة بالأدلة.
   - إرسال ملخص طبي (Executive Summary) + توصيات مفصلة (Recommendations) + قائمة المراجع بالصفحات (Verified Sources) + نسبة الثقة (Confidence Score).

---

## 🛠️ الأوامر المتاحة في البوت

| الأمر | الوظيفة |
| :--- | :--- |
| `/start` | عرض الترحيب بنظام VERA والتعريف بمهام النظام. |
| `/help` | عرض إرشادات الاستخدام وأمثلة للأسئلة الطبية النموذجية. |
| **أي سؤال طبي** | معالجة السؤال واسترجاع الإجابة من الإرشادات الطبية المعتمدة. |

---

## 🔍 فحص حالة وتشخيص الـ Webhook (Diagnostics)

### 1. التأكد من حالة الـ Webhook:
افتح الرابط في المتصفح أو أرسل طلب:
- `GET http://localhost:8000/telegram/webhook-info`
- يرجع عدد الرسائل المعالجة ورابط الـ Webhook المسجل حالياً لدى تيليجرام.

### 2. حذف الـ Webhook (عند الرغبة في إيقافه):
- `POST http://localhost:8000/telegram/remove-webhook`

---

## 🧪 اختبار التكامل بدون تيليجرام (Automated Tests)
للتأكد من أن جميع وظائف البوت وتنسيقات الرسائل وتجزئة النصوص تعمل بنسبة 100%:
```powershell
pytest tests/test_telegram.py -v
```

# ⚙️ Configuration Module (`config/`)

يحتوي هذا المجلد على ملفات الإعدادات المركزية لمنظومة **VERA**.

---

## 📁 محتويات المجلد

- `config.yaml`: ملف الإعدادات الرئيسي لجميع مراحل النظام (Ingestion, Retrieval, Generation, Safety, Evaluation).

---

## 🔧 الأقسام الرئيسية في `config.yaml`

| القسم | الوصف | الإعدادات الافتراضية |
| :--- | :--- | :--- |
| **`paths`** | مسارات البيانات، النماذج، وقواعد البيانات الشعاعية. | `./data/raw_pdfs`, `./data/vector_db` |
| **`ingestion`** | حجم التقطيع (`chunk_size`) ومقدار التداخل (`overlap`) واستراتيجية التقطيع. | `chunk_size: 600`, `chunk_overlap: 100` |
| **`embeddings`** | مزود وموديل التضمين (HuggingFace / OpenAI / Gemini). | `BAAI/bge-small-en-v1.5` |
| **`vector_store`** | نوع قاعدة البيانات الشعاعية والمقياس (`cosine`). | `chromadb`, `vera_clinical_guidelines` |
| **`retrieval`** | عدد النتائج المسترجعة (`top_k`)، نوع البحث (Hybrid / Dense)، ونسبة المطابقة. | `top_k: 4`, `search_type: hybrid` |
| **`generation`** | موديل التوليد ودرجة الحرارة (صفر لضمان الدقة وتجنب الهلوسة). | `gpt-4o-mini`, `temperature: 0.0` |
| **`safety`** | بوابات الأمان، عتبة الثقة (`confidence_threshold`)، والتحقق من الهلوسة. | `min_retrieval_confidence: 0.62` |
| **`evaluation`** | معايير التقييم الآلي وملفات الاختبار المرجعية. | `Precision@K`, `Faithfulness`, `RAGAS` |

---

## 💡 كيفية الاستخدام في الكود

```python
from src.config import load_config

config = load_config("config/config.yaml")
print(config.retrieval.top_k)
```

# 🧠 Embeddings & Vector Indexing (`src/embeddings/`)

مسؤول عن تحويل المقاطع النصية إلى متجهات رقمية (Embeddings) وبناء الفهرس الشعاعي الدائم.

---

## 🎯 المكونات الرئيسية

1. **`embedder.py`**:
   - واجهة توليد المتجهات بالاعتماد على نماذج رائدة مثل `BAAI/bge-small-en-v1.5` أو `sentence-transformers/all-MiniLM-L6-v2`.
   - دعم التطبيع الشعاعي (Cosine Normalization) وإضافة سياق الاستعلام (Query Instruction).

2. **`vector_store.py`**:
   - إدارة قاعدة البيانات الشعاعية الدائمة باستخدام `ChromaDB`.
   - تخزين النصوص مع بياناتها الوصفية كاملة (`doc_id`, `section`, `page_number`).
   - تحويل مسافات الجيب تمام (Cosine Distance) إلى درجات تشابه دقيقة (`similarity_score`).

---

## 🚀 كيفية التجربة والاختبار

انظر المفكرة التفاعلية:
`notebooks/02_embeddings_and_indexing.ipynb`

# 📓 Interactive Notebooks Suite (`notebooks/`)

تحتوي هذه الحزمة على 6 مفكرات تفاعلية (Jupyter Notebooks) متسلسلة خطوة بخطوة، ومصممة لمطابقة متطلبات أيام الهاكاثون الخمسة (Day 1 إلى Day 5).

---

## 🗺️ خريطة المفكرات التفاعلية

| المفكرة | اليوم المستهدف | الأهداف والوظائف |
| :--- | :--- | :--- |
| **`01_ingestion_and_chunking.ipynb`** | **Day 1** | قراءة وتفريغ ملفات الـ PDF، استخراج الجداول، التقطيع الواعي بالأقسام (Section-Aware)، وحفظ كتالوج المقاطع. |
| **`02_embeddings_and_indexing.ipynb`** | **Day 1–2** | توليد التضمين الشعاعي (Dense Embeddings)، وإنشاء قاعدة بيانات `ChromaDB` وتجربة الاستعلامات البسيطة. |
| **`03_retrieval_optimization.ipynb`** | **Day 2** | تحسين طبقة الاسترجاع، مقارنة البحث الشعاعي مع البحث الهجين (BM25 + Dense)، وضبط عتبات التطابق. |
| **`04_grounded_generation_citations.ipynb`** | **Day 3** | ربط التوليد الصارم بنماذج اللغة، هيكلة الإجابة، واستخراج وتدقيق الاستشهادات المرجعية `[Doc | Sec | Page]`. |
| **`05_safety_guardrails_evaluation.ipynb`** | **Day 4** | اختبار حواجز الأمان، كشف الهلوسة، رفض الأسئلة الخارجة عن النطاق، وتشغيل التقييم المعياري `Precision@K`. |
| **`06_end_to_end_demo_day5.ipynb`** | **Day 5** | العرض النهائي التفاعلي المباشر (Live Demo) أمام لجنة التحكيم لجميع الحالات (In-Scope, Out-of-Scope, Emergency). |

---

## 🚀 كيفية التشغيل

1. تأكد من تفعيل البيئة الافتراضية وتثبيت الحزم:
   ```bash
   pip install -r requirements.txt
   ```
2. شغّل خادم Jupyter:
   ```bash
   jupyter notebook
   ```
3. افتح المفكرات بالترتيب من `01` إلى `06`.

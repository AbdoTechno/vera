# 🎓 خارطة طريق مذاكرة وفهم مشروع VERA
### Interactive Step-by-Step Study Checklist

استخدم هذا الدليل كقائمة مهام تفاعلية (Checklist) خطوة بخطوة لمذاكرة المشروع وفهمه بعمق حتى تصبح جاهزاً لشرحه وعرضه باحترافية أمام لجنة التحكيم.

---

## 📌 المرحلة 1: فهم المفاهيم الأساسية وفكرة المشروع (الأساس النظري)

- [ ] **فهم فكرة الـ RAG ولماذا نحتاجه في الطب**:
  - [ ] فهم الفرق بين إجابة الذكاء الاصطناعي العادية وإجابة الـ RAG المعتمدة على ملفات الـ PDF.
  - [ ] فهم مبدأ المنظومة: `Fluent Answer ≠ Safe Answer` (الإجابة الفصيحة ليست بالضرورة آمنة).
- [ ] **قراءة الدليل الشامل والمبسط**:
  - [ ] قراءة ملف [`HOW_TO_RUN_AND_SYSTEM_GUIDE.md`](file:///d:/AI%20Hackathon/New%20data/HOW_TO_RUN_AND_SYSTEM_GUIDE.md).
  - [ ] مراجعة جدول المكتبات المستخدمة وسبب اختيار كل مكتبة (`pdfplumber`, `chromadb`, `rank_bm25`, `google-genai`).
- [ ] **التعرف على النطاق الطبي للمشروع**:
  - [ ] قراءة ملخص الإرشادات الطبية في [`docs/clinical_guideline_summary.md`](file:///d:/AI%20Hackathon/New%20data/docs/clinical_guideline_summary.md).
  - [ ] معرفة أساسيات مرض ضمور العضلات الشوكي (SMA)، والفرق بين جينات `SMN1` و `SMN2`، وأسماء الأدوية الثلاثة المعتمدة (`Nusinersen`, `Zolgensma`, `Risdiplam`).
  - [ ] فهم دور تقنية التسلسل الجيني طويل القراءة (`Long-Read Sequencing`) في كشف الطفرات والترتيبات الصبغية المعقدة.

---

## 🛠️ المرحلة 2: تجهيز البيئة وتشغيل الاختبارات (التجهيز العملي)

- [ ] **تثبيت حزم ومكتبات المشروع**:
  - [ ] فتح التيرمينال وتنفيذ: `pip install -r requirements.txt`.
- [ ] **التحقق من مفتاح Google Gemini API**:
  - [ ] فتح ملف [`.env`](file:///d:/AI%20Hackathon/New%20data/.env) والتأكد من وجود `GEMINI_API_KEY`.
- [ ] **تشغيل الاختبارات الآلية للتأكد من سلامة النظام**:
  - [ ] تنفيذ الأمر: `pytest -v` والتأكد من ظهور `6 passed` باللون الأخضر.

---

## 📓 المرحلة 3: المذاكرة العملية عبر المفكرات التفاعلية (Day 1 إلى Day 5)

افتح خادم Jupyter عبر التيرمينال: `jupyter notebook` وطبق المفكرات بالترتيب:

- [ ] **اليوم الأول — استخراج الـ PDFs والتقطيع الواعي**:
  - [ ] فتح مفكرة [`notebooks/01_ingestion_and_chunking.ipynb`](file:///d:/AI%20Hackathon/New%20data/notebooks/01_ingestion_and_chunking.ipynb).
  - [ ] فهم كيف يستخرج كود `pdfplumber` النصوص والجداول مع الحفاظ على رقم كل صفحة.
  - [ ] فهم كيف يقوم `MedicalChunker` بتقطيع النصوص بحسب عناوين الأقسام (`Section-Aware Chunking`).
  - [ ] رؤية ملف المقاطع الناتج في [`data/processed/chunk_catalog.json`](file:///d:/AI%20Hackathon/New%20data/data/processed/chunk_catalog.json).
- [ ] **اليوم الثاني (أ) — التضمين والفهرسة الشعاعية**:
  - [ ] فتح مفكرة [`notebooks/02_embeddings_and_indexing.ipynb`](file:///d:/AI%20Hackathon/New%20data/notebooks/02_embeddings_and_indexing.ipynb).
  - [ ] فهم كيف يحول موديل `bge-small` الكلمات إلى متجهات رقمية (Embeddings).
  - [ ] فهم كيفية تخزينها في قاعدة بيانات `ChromaDB` في ثوانٍ وتجربة بحث أولي.
- [ ] **اليوم الثاني (ب) — تحسين الاسترجاع والبحث الهجين**:
  - [ ] فتح مفكرة [`notebooks/03_retrieval_optimization.ipynb`](file:///d:/AI%20Hackathon/New%20data/notebooks/03_retrieval_optimization.ipynb).
  - [ ] مقارنة البحث الدلالي العادي (Dense Search) مع البحث الهجين (Dense + BM25).
  - [ ] فهم كيف يساعد قاموس المرادفات (`Query Expansion`) في ربط الأسماء التجارية (مثل Spinraza) بالأسماء العلمية (Nusinersen).
- [ ] **اليوم الثالث — التوليد المنضبط بالأدلة عبر Gemini والاقتباسات**:
  - [ ] فتح مفكرة [`notebooks/04_grounded_generation_citations.ipynb`](file:///d:/AI%20Hackathon/New%20data/notebooks/04_grounded_generation_citations.ipynb).
  - [ ] فهم صياغة البرومبت الصارم (`CLINICAL_SYSTEM_PROMPT`) الذي يحظر المعرفة الخارجية ويضبط درجة الحرارة `temperature = 0.0`.
  - [ ] تجربة توليد إجابة سريرية وملاحظة الاستشهادات الدقيقة بصيغة: `[Doc Name | Section | Page]`.
  - [ ] التحقق من دقة الاقتباسات برمجياً عبر `CitationFormatter`.
- [ ] **اليوم الرابع — حواجز الأمان، كشف الهلوسة، والتقييم المعياري**:
  - [ ] فتح مفكرة [`notebooks/05_safety_guardrails_evaluation.ipynb`](file:///d:/AI%20Hackathon/New%20data/notebooks/05_safety_guardrails_evaluation.ipynb).
  - [ ] تجربة سؤال خارج النطاق (مثل علاج السكر) ورؤية الرفض المنظم من `RefusalEngine`.
  - [ ] تجربة حالة طوارئ حرجة ورؤية رسالة الطوارئ الفورية.
  - [ ] تشغيل التقييم التلقائي على الأسئلة الذهبية وقياس `Precision@K` ونسبة الوفاء للنص `Faithfulness`.
- [ ] **اليوم الخامس — المفكرة التفاعلية المتكاملة (Live Demo Console)**:
  - [ ] فتح مفكرة [`notebooks/06_end_to_end_demo_day5.ipynb`](file:///d:/AI%20Hackathon/New%20data/notebooks/06_end_to_end_demo_day5.ipynb).
  - [ ] تجربة الدالة الشاملة `ask_vera(...)` التي تنفذ الـ 4 طبقات كاملة في أمر واحد.
  - [ ] التدرب على شرح كل جزء يظهر على الشاشة (جدول الأدلة، الإجابة، الاستشهادات، تدقيق الأمان).

---

## 💻 المرحلة 4: الغوص في الكود المصدري وفهم المعمارية (`src/`)

- [ ] **مراجعة طبقة الاستخراج [`src/ingestion/`](file:///d:/AI%20Hackathon/New%20data/src/ingestion/)**:
  - [ ] ملف `pdf_loader.py`: استخراج النصوص والجداول.
  - [ ] ملف `chunker.py`: استراتيجية التقطيع وتتبع عناوين الأقسام.
- [ ] **مراجعة طبقة التضمين والفهرسة [`src/embeddings/`](file:///d:/AI%20Hackathon/New%20data/src/embeddings/)**:
  - [ ] ملف `embedder.py`: واجهة توليد المتجهات.
  - [ ] ملف `vector_store.py`: إدارة كولكشن ChromaDB وحساب درجات التشابه.
- [ ] **مراجعة طبقة الاسترجاع [`src/retrieval/`](file:///d:/AI%20Hackathon/New%20data/src/retrieval/)**:
  - [ ] ملف `semantic_search.py`: البحث الدلالي مع عتبات الثقة.
  - [ ] ملف `hybrid_retriever.py`: دمج BM25 و Dense بخوارزمية RRF.
  - [ ] ملف `query_expansion.py`: قاموس المرادفات والمصطلحات الطبية.
- [ ] **مراجعة طبقة التوليد [`src/generation/`](file:///d:/AI%20Hackathon/New%20data/src/generation/)**:
  - [ ] ملف `prompt_templates.py`: قوالب التوجيه الطبي الصارم.
  - [ ] ملف `generator.py`: الربط مع Gemini API (أو الوضع المحلي الاحتياطي).
  - [ ] ملف `citation_formatter.py`: فحص واستخراج الاقتباسات.
- [ ] **مراجعة طبقة الأمان السريري [`src/safety/`](file:///d:/AI%20Hackathon/New%20data/src/safety/)**:
  - [ ] ملف `confidence_gate.py`: فحص درجة التشابه (أعلى من `0.60`).
  - [ ] ملف `refusal_engine.py`: الرفض الآمن والتنبيه الطبي القانوني.
  - [ ] ملف `hallucination_checker.py`: كشف الادعاءات غير الموثقة.
- [ ] **مراجعة طبقة التقييم [`src/evaluation/`](file:///d:/AI%20Hackathon/New%20data/src/evaluation/)**:
  - [ ] ملف `retrieval_metrics.py`: حساب Precision و Recall و MRR.
  - [ ] ملف `benchmark_runner.py`: المشغل الآلي لاختبارات الـ Benchmark.

---

## 🏆 المرحلة 5: الاستعداد النهائي للعرض والتحكيم (Presentation Prep)

- [ ] **مراجعة المخططات المعمارية**:
  - [ ] فتح [`docs/architecture_diagrams.md`](file:///d:/AI%20Hackathon/New%20data/docs/architecture_diagrams.md) وفهم مخطط الـ 4 طبقات ومخطط الـ Sequence Diagram.
- [ ] **مراجعة جدول الـ 100 درجة للجنة التحكيم**:
  - [ ] فتح [`docs/judging_rubric_alignment.md`](file:///d:/AI%20Hackathon/New%20data/docs/judging_rubric_alignment.md) ومعرفة أين توجد متطلبات كل معيار:
    - [ ] Retrieval Quality (30 pts)
    - [ ] Grounding & Citations (25 pts)
    - [ ] System Architecture (15 pts)
    - [ ] Evaluation Rigor (15 pts)
    - [ ] Clinical Safety (10 pts)
    - [ ] UX / Live Demo (5 pts)
- [ ] **التدرب على العرض الحي (Mock Presentation)**:
  - [ ] فتح مفكرة `notebooks/06_end_to_end_demo_day5.ipynb` وتشغيل الأسئلة التجريبية بسلاسة.
  - [ ] التدرب على شرح الرفض الآمن عندما يطلب المحكم سؤالاً خارج النطاق.

---
🎯 **بإتمامك لهذه الخارطة، ستكون قد أتقنت المشروع نظرياً وعملياً وبرمجياً 100%!**

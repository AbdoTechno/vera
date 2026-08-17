# 🏆 VERA Alignment with Judging Rubric (100 Points)

دليل مطابقة منظومة **VERA** المباشرة مع معايير تقييم لجنة التحكيم الرسمية في الهاكاثون.

---

## 📊 جدول الدرجات ومطابقة الكود البرمجي

| المعيار | الدرجة | متطلبات التقييم | أين تقع في مشروع VERA؟ |
| :--- | :---: | :--- | :--- |
| **1. Retrieval Quality** | **30** | دقة البحث الدلالي، Top-K، البحث الهجين، التقطيع الواعي بالأقسام. | `src/retrieval/`, `src/ingestion/chunker.py`, `notebooks/03_retrieval_optimization.ipynb` |
| **2. Grounding & Citations** | **25** | التوليد المنضبط بالوثائق، وجود استشهادات دقيقة `[Doc \| Sec \| Page]`، ومطابقتها. | `src/generation/`, `src/generation/citation_formatter.py`, `notebooks/04_grounded_generation_citations.ipynb` |
| **3. System Architecture** | **15** | بناء الطبقات الأربع (Ingestion, Retrieval, Generation, Safety)، نظافة الكود والتصميم. | `src/` كاملة مقسمة بوضوح مع ملفات `README.md` ومخططات `docs/architecture_diagrams.md`. |
| **4. Evaluation Rigor** | **15** | قياس Precision@K، Recall، Faithfulness، وتشغيل اختبارات معيارية على Gold QA. | `src/evaluation/`, `eval_datasets/`, `notebooks/05_safety_guardrails_evaluation.ipynb` |
| **5. Clinical Safety** | **10** | كشف الهلوسة، عتبة الثقة، رفض الأسئلة خارج النطاق، والتنبيه السريري. | `src/safety/`, `confidence_gate.py`, `refusal_engine.py`, `hallucination_checker.py` |
| **6. UX / Live Demo** | **5** | عرض تفاعلي مباشر واضح للمحكمين، شفافية عرض المقاطع المسترجعة. | `notebooks/06_end_to_end_demo_day5.ipynb` مع جداول تفاعلية جاهزة للأسئلة المباشرة. |
| **المجموع** | **100** | **أعلى معايير التميز الهندسي والسريري** | ✅ **تغطية شاملة 100/100** |

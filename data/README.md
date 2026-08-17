# 📚 Data Management Module (`data/`)

مجلد إدارة البيانات لمشروع **VERA**، ويشمل دورة حياة المستندات الطبية من ملفات الـ PDF الأصلية وحتى النصوص المهيكلة وقواعد المعرفة.

---

## 🗂️ الهيكل التنظيمي للمجلد

```
data/
├── raw_pdfs/             # ملفات الإرشادات والأبحاث الطبية الرسمية (PDFs)
├── processed/            # النصوص المستخرجة، الجداول، ومقاطع النصوص المهيكلة (JSONs)
├── knowledge_base/       # قواعد المعرفة النصية الشاملة بصيغة Markdown
└── vector_db/            # قاعدة البيانات الشعاعية المخزنة محلياً (ChromaDB / FAISS)
```

---

## 📋 نظرة عامة على المجلدات الفرعية

1. **`raw_pdfs/`**:
   - يحتوي على الأبحاث والإرشادات الطبية المعتمدة (مثل إرشادات الضمور العضلي الشوكي SMA وأبحاث تسلسل الجينوم).
   - انظر [raw_pdfs/README.md](file:///d:/AI%20Hackathon/New%20data/data/raw_pdfs/README.md).

2. **`processed/`**:
   - يحتوي على نواتج المعالجة والاستخراج الأولي للنصوص والتقطيع المهيكل بحسب الأقسام وأرقام الصفحات.
   - انظر [processed/README.md](file:///d:/AI%20Hackathon/New%20data/data/processed/README.md).

3. **`knowledge_base/`**:
   - يحتوي على قاعدة المعرفة الطبية الموحدة والمفهرسة بروابط للمستندات والصفحات.
   - انظر [knowledge_base/README.md](file:///d:/AI%20Hackathon/New%20data/data/knowledge_base/README.md).

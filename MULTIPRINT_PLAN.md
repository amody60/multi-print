# PLAN.md — مشروع Multi Print (طباعة دفعية متعددة الملفات)

**Protocol:** IDEAgent v3.2
**Archive Type:** FULL (مشروع جديد، مفيش `PROJECT_MAP.json` سابق)
**Stage الحالية:** Stage 3 → Stage 4 (جاهزين للـ Owner يراجع ويقول `STAGE 4 — PLAN APPROVED`)
**Owner:** محمد
**IDE Agent:** Codex Agent (VS Code)

---

## Stage 0 — Task Definition (Prompt 1)

عايزين برنامج ديسكتوب اسمه **Multi Print** يعمل الآتي:

1. تاخد أكتر من ملف مختلف (PDF / Word / PowerPoint / صور) وتطبعهم **كل ملف Print Job لوحده** — من غير ما محتوى الملفات يتخلط ببعضه.
2. لكل ملف/دفعة إعدادات طباعة منفصلة:
   - N-up: كام سلايد في الورقة (2 / 4 / 6 / 8 / 10)
   - وش بس ولا وش وضهر (Simplex / Duplex)
   - ألوان ولا أبيض وأسود
   - عدد النسخ
3. **ميزة المجموعات (Printer Groups):** تعمل جروب فيه أكتر من طابعة. أول ما تدوس زرار الطباعة، تختار الجروب — وبعدها اختيار الطابعة المفردة يختفي لأن الجروب هو اللي بيوزع الشغل على الطابعات اللي جواه (round-robin زي اللي كان في multiprint القديم).
4. **Settings:** كل بيانات الطابعات (الاسم، النوع، هل بتدعم Duplex، مقاس الورق الافتراضي...) تتعدل من هنا.
5. **أول تشغيل (First Run):** إعدادات بدائية — مقاس ورق افتراضي، طابعة أساسية، وطابعة تانية احتياطية يقدر يبدّل عليها بسرعة من غير ما يدخل Settings.
6. **Preview:** يعرض الملفات قبل الطباعة، تقدر تعمل Scroll بين الصفحات، والصفحة تبقى Fit في الورقة (مفيش هوامش بيضا كبيرة).
7. **صيغ الملفات المدعومة:** PDF, DOCX, PPTX, صور (JPG/PNG).

---

## Stage 0.5 — File Coverage Check

| البند | الحالة |
|---|---|
| Source code سابق | **مش موجود** — مشروع جديد من الصفر |
| `PROJECT_MAP.json` | مش موجود — غياب متعمد لأنه أول Archive |
| Archive Type | **FULL** (معلن) |
| ملفات إعداد/Config سابقة | مفيش |
| خطط سابقة | الملف اللي انت رفعته (بروتوكول IDEAgent v3.2 نفسه) |

مفيش بند Critical ناقص — المشروع بيبدأ من الصفر رسميًا، فمفيش أرشيف مطلوب أجمعه.

⚠️ ملاحظة مهمة: في الذاكرة عندي إنك بنيت 3 محاولات سابقة لنفس الفكرة تقريبًا (`multiprint` بـ Python/CustomTkinter، بعدين `PrintFlow` بـ Electron، وبعدين `Multi Print` .exe تاني بـ Python). **الخطة دي بتفترض إننا بنبدأ مشروع رابع نضيف عليه الميزات الجديدة (N-up composition, Groups, Preview بالشكل ده) — مش بنكمل على كود قديم موجود.** لو انت فعليًا عايز نكمل على أي كود من التلاتة دول، ده لازم يتقال قبل ما الـ Codex Agent يبدأ ينفذ، لأنه هيغيّر الـ Archive Type لـ INCREMENTAL وهيغيّر Scope Lock بالكامل.

---

## Assumption Table

| ID | الوصف | Severity | Impact لو غلط | Status |
|---|---|---|---|---|
| A-01 | المشروع بيبدأ من الصفر (مش كومنيويشن على `PrintFlow` أو `multiprint` القديم) | Critical | لو غلط، هيتغير الـ Scope Lock كله | **Resolved** — أكّدت "من الصفر" |
| A-02 | الـ Backend **Python**، والـ Frontend **مش CustomTkinter** — هيكون HTML/CSS/JS معروض جوه نافذة Desktop عبر **pywebview**، والـ Python بيشغّل كل حاجة (الطباعة، التحويل، الاكتشاف) كـ local API. السبب: عايز شكل حلو وده مش متاح بشكل كويس في CustomTkinter، وفي نفس الوقت مش عايزين تعقيد/حجم Electron + Node كامل | Critical | لو تفضل Stack تاني للواجهة (زي Tauri أو Electron فعلي)، هيتغير الـ packaging والـ IPC layer | **Resolved** — بناءً على ردك (Python backend + حاجة تانية للفرونت) |
| A-03 | الطباعة الفعلية هتبقى عبر **SumatraPDF.exe** (subprocess من بايثون) بعد ما أي صيغة تتحول PDF — لأنه بيدعم Duplex/N-copies من الـ command line بسهولة وده كان شغال كويس في `PrintFlow` | Minor | لو مش عايز تعتمد على أداة خارجية، البديل الطباعة الخام عبر `win32print` (تحكم أدق بس تعقيد أكتر في التعامل مع PDF) | Open |
| A-04 | تحويل DOCX/PPTX لـ PDF هيبقى عبر **LibreOffice headless** (subprocess) — بايثون بينده بنفس الطريقة اللي كانت شغالة في PrintFlow | Minor | لو مش عايز تعتمد على LibreOffice، البديل أبطأ (`docx2pdf` محتاج MS Office مثبت) | Open |
| A-05 | الـ N-up composition (2/4/6/8/10 صفحات في ورقة) هيتعمل بـ **PyMuPDF (fitz)** أو **pypdf** بدل `pdf-lib` (المكافئ في بايثون) | Minor | لو الصفحات أحجامها مختلفة جوه نفس الملف، هيحتاج معالجة إضافية للـ scaling | Open |
| A-06 | نظام الـ Round-Robin على الـ Printer Group هيكون **نفس منطق `multiprint` القديم** (توزيع الملفات بالتبادل على الطابعات جوه الجروب) | Minor | لو عايز خوارزمية توزيع مختلفة (مثلاً حسب الحمل الفعلي) ده هيبقى تعقيد إضافي | Open |
| A-07 | البرنامج شغال على **Windows فقط** (زي كل نسخك السابقة) | Critical | لو محتاجه Cross-platform هيتغير كل حاجة متعلقة بالـ printing backend | **Resolved** — مفيش اعتراض، هيفضل Windows-only |
| A-08 | الطابعات الحقيقية عندك (5 طابعات HP/Xerox من ضمن 16 جهاز ظاهر في الـ OS) هي نفسها هتتستخدم في التطوير والاختبار | Minor | لو تغيّر عدد/نوع الطابعات، إعدادات الـ Duplex/الألوان الافتراضية هتحتاج مراجعة | Open |
| A-09 | اكتشاف الطابعات هيتم عبر **`win32print.EnumPrinters`** — بيرجع كل الطابعات المربوطة/المثبتة فعليًا على الجهاز (محلية + شبكة)، وده اللي طلبته صراحة | Critical | لو فيه طابعات شبكة مش ظاهرة بالطريقة دي، هنحتاج طريقة اكتشاف إضافية (WMI) | **Resolved** — بناءً على طلبك المباشر |

**كل الـ Critical Assumptions اتحلت.** باقي بس Minor items بتتراجع أثناء التنفيذ لو ظهرت مشكلة فعلية فيهم.

---

## Confidence Score

```
Overall Confidence: 90%
Architecture: 92%   (Python backend + pywebview مسار واضح ومطابق لخبرتك في FastAPI)
Dependencies: 85%   (SumatraPDF / LibreOffice لازم يتأكد وجودهم أو يتثبتوا)
Business Logic: 90% (منطق الـ Groups والـ Round-Robin واضح من التجربة القديمة)
```

الرقم ده تقديري وصفي بس — مش بوابة PASS/FAIL. الأساس الحقيقي هو الـ Assumption Table فوق.

---

## Architecture & Tech Stack (محدّثة بعد ردك)

**الفكرة الأساسية:** Backend بايثون كامل (فيه كل منطق الطباعة/التحويل/الاكتشاف)، وواجهة **HTML/CSS/JS** بتصميم عصري، معروضة جوه نافذة Desktop حقيقية عن طريق **pywebview** — يعني مفيش متصفح ظاهر، وشكلها زي أي تطبيق Desktop عادي، بس التصميم حر بالكامل زي أي موقع (خط، ألوان، أنيميشن... إلخ) عكس محدودية CustomTkinter.

ليه pywebview تحديدًا وملهاش Electron؟
- خفيف جدًا مقارنة بـ Electron (مفيش Chromium كامل متضمن، بيستخدم WebView2 الموجود في ويندوز أصلاً).
- بايثون هو اللي بيتحكم في كل حاجة مباشرة (مفيش IPC بين process ونود زي Electron) — وده مناسب أكتر لخبرتك في FastAPI/Python.
- تقدر توصل الواجهة بالـ backend بطريقتين: إما `pywebview` JS API مباشرة، أو تشغّل FastAPI على `localhost` وتوديها من جواه (أفضل لو حابب تختبر الـ API لوحدها من الـ browser وقت التطوير).

**القرار:** هنشغّل **FastAPI** على `127.0.0.1` (Uvicorn) كـ backend حقيقي، و`pywebview` بيفتح نافذة بتحمّل الواجهة من عليه. كده الواجهة والباك إند منفصلين تمامًا وسهل تتابعهم لوحدهم، وبرضو تقدر تفتح نفس الواجهة من متصفح عادي وقت التطوير للتجربة السريعة.

```
multi-print/
├── backend/
│   ├── main.py                     # نقطة الدخول: يشغّل FastAPI + يفتح نافذة pywebview
│   ├── api/
│   │   ├── files.py                 # رفع/إدارة الملفات في الـ Queue
│   │   ├── printers.py              # Endpoints لقراءة الطابعات وإدارة المجموعات
│   │   ├── settings.py              # Endpoints للإعدادات + First Run
│   │   └── print_jobs.py            # بدء الطباعة (Job لكل ملف)
│   ├── printers/
│   │   ├── discovery.py             # win32print.EnumPrinters() — اكتشاف الطابعات الحقيقية
│   │   ├── groups.py                # منطق Printer Groups + Round-Robin
│   │   └── print_queue.py           # إدارة كل Print Job لوحده (Thread/Queue منفصلة لكل Job)
│   ├── convert/
│   │   ├── to_pdf.py                # DOCX/PPTX → PDF عبر LibreOffice headless (subprocess)
│   │   └── image_to_pdf.py          # صور (JPG/PNG) → PDF
│   ├── compose/
│   │   └── n_up.py                  # تركيب N-up (2/4/6/8/10) عبر PyMuPDF/pypdf + fit-to-page
│   ├── config/
│   │   ├── settings_store.py        # قراءة/كتابة settings.json
│   │   └── first_run.py             # منطق First Run Wizard
│   └── resources/
│       └── bin/                     # SumatraPDF.exe مرفق مع البرنامج
├── frontend/
│   ├── index.html
│   ├── pages/
│   │   ├── main-queue.html          # قائمة الملفات + إعدادات كل ملف
│   │   ├── print-dialog.html        # اختيار طابعة/جروب وقت الطباعة
│   │   ├── preview.html             # المعاينة بالـ Scroll + Fit-to-page
│   │   └── settings.html            # صفحة الإعدادات
│   ├── css/
│   │   └── style.css                # تصميم عصري (Dark/Light، خط واضح، مسافات مريحة)
│   └── js/
│       ├── api.js                   # اتصال بالـ FastAPI (fetch/WebSocket)
│       └── ...
├── PROJECT_MAP.json                 # هيتولّد بعد Stage 6 PASS الأول
├── requirements.txt
└── build.spec                       # PyInstaller لتحويله .exe واحد

---

## تفصيل الميزات (Functional Spec)

### 1) قائمة الطباعة (Batch Queue)
- تسحب/تضيف أكتر من ملف (PDF/DOCX/PPTX/صور).
- كل ملف صف لوحده فيه: اسم الملف، عدد صفحاته، وأيقونة الصيغة.
- بجانب كل ملف: N-up / Duplex-Simplex / لون-أبيض وأسود / عدد نسخ — قابلة للتعديل individually.
- زرار "طباعة الكل" يبعت كل ملف كـ Job منفصل تمامًا للـ Print Queue — الملفات ميتخلطوش في بعض.

### 2) Printer Groups
- شاشة "إدارة المجموعات": تعمل جروب، تسميه، تضيف له أكتر من طابعة حقيقية.
- وقت الطباعة: تختار "اطبع على مجموعة" → تختار اسم الجروب فقط → قائمة الطابعات المفردة **تختفي تلقائيًا** لأن الجروب هيوزع الملفات Round-Robin على الطابعات اللي جواه.
- لو مفيش جروب متعمل، الخيار الافتراضي يفضل طابعة مفردة عادية.

### 3) Settings
- تعديل بيانات كل طابعة (تدعم Duplex؟ تدعم ألوان؟ مقاس ورق افتراضي؟).
- إدارة المجموعات (إضافة/حذف طابعة من جروب).
- تغيير الطابعة الأساسية/الاحتياطية.

### 4) First Run Wizard
- أول ما البرنامج يتفتح لأول مرة: يسأل عن مقاس الورق الافتراضي، الطابعة الأساسية، والطابعة الاحتياطية (Fallback) — يقدر يبدّل عليها من غير ما يدخل Settings كل مرة.

### 5) Preview
- معاينة كل ملف قبل الطباعة، تقدر تعمل Scroll بين الصفحات.
- الصفحة تتعرض Fit-to-page — يعني بعد تركيب الـ N-up، مفيش هوامش بيضا كبيرة حوالين المحتوى.

### 6) دعم الصيغ
- PDF: يتقرأ مباشرة.
- DOCX/PPTX: يتحول PDF أولًا عبر LibreOffice headless.
- صور (JPG/PNG): تتحول صفحة PDF واحدة (مع الحفاظ على الـ aspect ratio) قبل أي تركيب N-up.

---

## Stage 3 — Workflow Planning (تقسيم المهام)

| Task | الوصف | Dependency |
|---|---|---|
| T-01 | إعداد هيكل مشروع Electron + TypeScript + إعداد الـ IPC الأساسي | — |
| T-02 | Printer Discovery: قراءة الطابعات المتصلة بالـ Windows | T-01 |
| T-03 | Settings Store + First Run Wizard | T-01, T-02 |
| T-04 | Convert Layer: DOCX/PPTX → PDF (LibreOffice) + صور → PDF | T-01 |
| T-05 | N-up Composition (pdf-lib) + Fit-to-page | T-04 |
| T-06 | Print Queue: كل ملف Job منفصل عبر SumatraPDF (Simplex/Duplex, ألوان, نسخ) | T-02, T-05 |
| T-07 | Printer Groups + منطق Round-Robin | T-02, T-06 |
| T-08 | UI: MainQueue + إعدادات لكل ملف | T-01 |
| T-09 | UI: PreviewPane (Scroll + Fit-to-page) | T-05, T-08 |
| T-10 | UI: PrintDialog (اختيار طابعة/جروب، اختفاء القائمة بعد اختيار جروب) | T-07, T-08 |
| T-11 | UI: SettingsPage | T-03, T-07 |
| T-12 | Packaging (.exe) + اختبار على الطابعات الحقيقية الخمسة | كل ما سبق |

الترتيب ده بيحترم dependency order: مفيش UI قبل ما الـ backend logic (convert/compose/print/groups) يبقى جاهز.

---

## Risk Register

| ID | الوصف | Severity | Impact | Status |
|---|---|---|---|---|
| R-01 | LibreOffice headless ممكن يبقى بطيء مع ملفات PPTX كبيرة أو فيها خطوط مش متثبتة | Medium | تأخير في التحويل، احتمال فقدان تنسيق | Open |
| R-02 | SumatraPDF لازم يتوفر كـ binary مرفق مع البرنامج (licensing/توزيع) | Medium | لو مش موجود وقت التوزيع، الطباعة تفشل بالكامل | Open |
| R-03 | الـ 16 جهاز ظاهر في الـ OS مش كلهم طابعات حقيقية — لازم فلترة صح وقت الـ Discovery | High | لو الفلترة غلط، هيظهر أجهزة وهمية (Fax, PDF printer) في القوائم | Open — **يحتاج تأكيدك** |
| R-04 | N-up composition مع ملفات مختلطة الاتجاه (Portrait/Landscape) | Medium | تخطيط غير متسق داخل نفس الجروب من الصفحات | Open |

R-03 محتاج موافقتك الصريحة لأنه High.

---

## Stage 4 — Plan Validation (Checklist)

- [ ] A-01, A-02, A-07 (Critical) لازم تتحل — **محتاجين تأكيدك**
- [x] Assumption Table كاملة ومنقولة للخطة
- [x] Dependency order في Stage 3 متطابق مع البنية المقترحة
- [ ] R-03 (High) — محتاج موافقتك الصريحة
- [x] Confidence Score اتراجع (وصفي بس، مش بوابة)

**الخطة معلقة (PENDING)** لحد ما ترد على النقط دي. أول ما تأكد، ابعتلي رسالة فيها `"STAGE 4 — PLAN APPROVED"` وساعتها الـ Codex Agent يبدأ Stage 5 (التنفيذ) على الـ Scope Lock المذكور فوق بالظبط.

---

## أسئلة محتاجة ردك عليها قبل الموافقة

1. نبدأ مشروع رابع من الصفر (Electron) — ولا تفضل نكمل على أي كود من التلات محاولات السابقة (`multiprint` / `PrintFlow` / `Multi Print` .exe)؟
2. تأكيد إن الـ Stack هيكون Electron + Node.js زي `PrintFlow` (مش Python/CustomTkinter تاني)؟
3. الـ 16 جهاز الظاهرين في نظام التشغيل — عايز فلترة تلقائية تستبعد الأجهزة الوهمية (زي "Microsoft Print to PDF" أو الفاكسات)، ولا عايز تحدد الـ 5 طابعات الحقيقية يدويًا من الـ Settings أول مرة؟

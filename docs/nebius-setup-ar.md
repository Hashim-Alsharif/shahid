# التسجيل وتفعيل Token Factory وأول استدعاء Nemotron

آخر مراجعة للوثائق الرسمية: 22 أكتوبر 2026. هذه خطوات تنفذها بحسابك؛
إنشاء ملفات المشروع لا يعني أن حساب Nebius أو الرصيد أو الاستدعاء أصبح جاهزًا.

## 1. الانضمام للهاكاثون

1. افتح https://nebiusglobalaihackathon.devpost.com/ وسجل دخول Devpost.
2. اضغط Join hackathon إذا لم تكن انضممت بعد. استخدم حسابك الحالي.
3. مشروعنا اسمه المبدئي `Shahid — Evidence-Based Web Log Triage`، والمسار
   Best Apps and Agents. إنشاء صفحة المشروع يمكن إكماله لاحقًا.

التسجيل في Devpost منفصل عن إنشاء حساب Token Factory.

## 2. إنشاء حساب Token Factory

1. افتح https://tokenfactory.nebius.com/.
2. سجل الدخول باستخدام Google أو GitHub وفق الخيارات المعروضة.
3. أكمل بيانات الحساب وإقرارات الخدمة بنفسك. إذا طُلب Organization أو
   Project فيمكن تسميته `shahid`؛ اختر المشروع نفسه عند إنشاء المفتاح.
4. استخدم بلد إقامتك الصحيح. إذا لم يكن متاحًا أو تعطل التفعيل، تذكر FAQ
   الرسمي أن بعض الدول لديها مشكلة تجهيز حسابات؛ اطلب مساعدة Nebius من
   رابط Discord في FAQ، ولا تختَر بلدًا مختلفًا لتجاوزها.

الهدف هو الوصول إلى لوحة Token Factory التي فيها Models / Playground
وAPI keys، وليس حجز خادم GPU أو إنشاء Dedicated Endpoint.

## 3. رصيد الهاكاثون

صفحة Resources الرسمية تعرض طلب 25 دولارًا من رصيد Token Factory عبر نموذج
طلب الرصيد. افتح الرابط الرسمي التالي (الكود مُعبأ مسبقًا في الرابط):

https://nebius.com/promo-code?utm_promo_activation_code=NEBIUS-DEVPOST-GLOBAL26&utm_promo_code_type=Token_Factory&utm_promo_event_code=2026-devpost-global-ai-hack

الكود التالي هو Activation code داخل نموذج الطلب، وليس كود شحن مباشر
لنافذة Top up balance. رُفض عند تجربته في نافذة الشحن:

```text
NEBIUS-DEVPOST-GLOBAL26
```

ويعرض 25 دولارًا إضافية عبر Nebius Builder Program:
https://dev.nebius.com/builders

1. أغلق نافذة Top up balance إن كانت مفتوحة، ثم افتح نموذج الطلب أعلاه.
2. أدخل اسمك وبريد حساب Token Factory نفسه، واختر المسمى المناسب لواقعك.
   النموذج يطلب Company name؛ للمشارك المستقل يمكن توضيح Independent developer.
   الهاتف وموقع الشركة لا تظهر بجانبهما علامة الإلزام عند المراجعة.
3. تحقق من حقل Activation code. خانات تلقي المعلومات التسويقية اختيارية.
4. راجع البيانات وموافقة معالجة البيانات المكتوبة بجوار Submit، ثم قدم الطلب
   بنفسك إذا وافقت عليها. النموذج يوضح أنه طلب للحصول على promotional code.
5. تابع رسالة التأكيد وبريدك وتعليمات الكود الذي يصلك؛ لا نفترض زمن تفعيل
   أو ظهور رصيد حتى نتحقق منه بحسابك. لا تعد إدخال Activation code في الشحن.

إذا لم تجد طريقة استخدام الكود، أرسل صورة الصفحة خالية من البيانات
المالية والأسرار لنحدد الخطوة حسب واجهتك. طلبات الرصيد المتعثرة يعالجها
دعم Nebius حالة بحالة وفق FAQ الرسمي. تحقق من الرصيد وحدود الاستخدام قبل
طلب الاستدلال؛ أسعار النماذج تختلف ولا يوجد وعد بتكلفة ثابتة لكل طلب.

## 4. إنشاء API key

1. من المشروع المقصود في Token Factory، افتح API keys.
2. اضغط Create API key / Get API key حسب الواجهة.
3. الاسم المقترح: `shahid-local`.
4. أنشئه واحفظ قيمته محليًا فورًا؛ الوثائق تقول إنه لا يمكن عرضه لاحقًا.
5. لا ترسل المفتاح في المحادثة أو صورة، ولا تضعه في وصف Devpost أو في Git.

## 5. وضع المفتاح في المشروع

من PowerShell:

```powershell
Set-Location -LiteralPath "C:\Users\Hashim Alsharif\Desktop\Hackathons\Nebius & NVIDIA Global"
notepad .env
```

تم تجهيز الملف المحلي `.env` فارغ المفتاح في بداية المشروع. إذا كنت تنشئ
نسخة جديدة ولم يوجد الملف، انسخ `.env.example` إلى `.env` أولًا؛ لا تستبدل
ملفًا سبق أن وضعت مفتاحك فيه.

ستجد:

```dotenv
NEBIUS_API_KEY=
NEBIUS_BASE_URL=https://api.tokenfactory.nebius.com/v1/
NEBIUS_MODEL=
```

الصق المفتاح بعد `NEBIUS_API_KEY=` ثم احفظ وأغلق Notepad. لا ترسل محتوى
هذا الملف لنا. يمكن ترك NEBIUS_MODEL فارغًا حتى خطوة عرض النماذج.
إذا أعطاك Playground رابط API إقليميًا، استخدم الرابط الرسمي من حسابك.

## 6. التأكد محليًا من الإعداد

البيئة والحزم جُهزت في هذا الجهاز. عند إعداد نسخة أخرى:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

ثم:

```powershell
.\.venv\Scripts\python.exe -m scripts.nebius_check --check-config
```

نجاح هذه الخطوة يعني أن المفتاح موجود وشكل الإعداد صحيح محليًا، وليس أنه
مقبول لدى Nebius؛ لا يُرسل فيها طلب شبكة.

## 7. عرض أسماء Nemotron الفعلية

```powershell
.\.venv\Scripts\python.exe -m scripts.nebius_check --models
```

هذا GET إلى قائمة النماذج في Token Factory. انسخ أحد معرّفات NVIDIA
Nemotron كما ظهر تمامًا، بحالة الأحرف نفسها، إلى NEBIUS_MODEL في `.env`.
نفضّل نموذجًا نصيًا من فئة Nano أو Lightning المتاحين في حسابك كبداية،
بعد مراجعة سعره. لا تختَر Omni المخصص أو نموذجًا من مزود آخر بالخطأ.

وجود النموذج بالقائمة لا يثبت أنه متاح للاستدلال بهذا الحساب؛ الخطوة
التالية هي الاختبار الفعلي. إذا لم تظهر نماذج Nemotron، نراجع صلاحيات
المشروع والرابط والتفعيل، ولا نبدّل لمزود خارج Nebius.

## 8. أول طلب حقيقي

بعد حفظ المعرّف:

```powershell
.\.venv\Scripts\python.exe -m scripts.nebius_check --chat
```

الأداة ترسل طلبًا واحدًا قصيرًا يطلب عبارة `Shahid connection OK.`. لا
ترسل سجلاتك. ميزانية الإخراج القصوى 1024 token؛ بعض النماذج تستخدم جزءًا
منها للاستدلال. يُستهلك الرصيد بحسب الاستخدام الفعلي ولا توجد إعادة تلقائية.

نعتبر الاتصال ناجحًا إذا ظهر `Live inference: PASS` واسم Nemotron وإجابة
نهائية غير فارغة. قد تختلف الإجابة عن العبارة المطلوبة؛ نجاح الاتصال
لا يقيس جودة تحليل السجلات. الدليل يُحفظ في:

```text
reports/nebius/smoke-last.json
```

يتضمن النموذج والإجابة والاستخدام والوقت، ولا يتضمن المفتاح. نجاح الاختبارات
المحلية بمحاكاة HTTP لا يحل محل هذا الدليل.

## تشخيص الأخطاء

| النتيجة | الخطوة التالية |
| --- | --- |
| Add NEBIUS_API_KEY | أضف المفتاح في .env داخل هذا المشروع |
| HTTP 401 | راجع المفتاح والمشروع الذي أنشأته فيه |
| HTTP 402 | راجع تفعيل الرصيد والفوترة |
| HTTP 403 | راجع صلاحيات المشروع وتفعيل الحساب وإتاحة النموذج |
| HTTP 404 | طابق عنوان API ومعرّف النموذج مع حسابك |
| HTTP 429 | راجع الحدود والرصيد قبل تكرار الطلب |
| Timeout | راجع الاستخدام أولًا؛ قد يكون الطلب وصل رغم مهلة العميل |
| No final answer | قد انتهت ميزانية النموذج قبل الإجابة؛ نراجع إعداداته قبل المحاولة التالية |

يمكن إرسال نص الخطأ الآمن الذي تطبعه الأداة. لا ترسل الملف `.env` أو
رؤوس Authorization أو لقطة يظهر فيها المفتاح.

## تجربة «شاهد» محليًا الآن

هذه الخطوة تعمل حتى قبل إنشاء حساب Nebius:

```powershell
.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8010
```

افتح http://127.0.0.1:8010/، اختر «محاولات دخول متكررة»، ثم «حلّل السجل
محليًا»، وبعدها اضغط رقم سطر الدليل. هذا الجزء يعمل بقواعد محلية فقط.
أصبح تفسير Nemotron الاختياري متاحًا داخل الواجهة بعد إعداد المفتاح والنموذج:
راجع docs/try-shahid-ar.md لخطوات المعاينة والإرسال وتبديل العربية/الإنجليزية.

## المصادر الرسمية

- https://docs.tokenfactory.nebius.com/quickstart
- https://docs.tokenfactory.nebius.com/api-reference/introduction
- https://api.tokenfactory.nebius.com/docs
- https://nebiusglobalaihackathon.devpost.com/updates/46203-kickoff-tips
- https://nebiusglobalaihackathon.devpost.com/resources
- https://nebiusglobalaihackathon.devpost.com/details/faqs
- https://dev.nebius.com/builders

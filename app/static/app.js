"use strict";
const $ = id => document.getElementById(id);
const node = (tag, text, cls) => { const el = document.createElement(tag); el.textContent = text; if(cls) el.className = cls; return el; };
const strings = {
  ar: {
    logout:"تسجيل الخروج", demoPrivacy:"تُرسل السجلات إلى خادم شاهد للتحليل بالقواعد. لا يحفظ التطبيق محتواها، لكنه يحتفظ بعدّادات الاستخدام وجلسات الدخول. استخدم العينات المصطنعة أولًا.",
    demoUsage:"المحاولات المتبقية: للجلسة {session} · للموقع اليوم {daily} · للموقع إجمالًا {total}. التجديد اليومي بتوقيت UTC. المحاولات الفاشلة تُحتسب أيضًا.",
    ai_disabled:"التفسير متوقف مؤقتًا لدى صاحب المشروع. التحليل بالقواعد ما زال متاحًا.", quota_exhausted:"وصلت التجربة إلى حد المحاولات. التحليل بالقواعد ما زال متاحًا؛ راجع صاحب المشروع إذا احتجت محاولات إضافية.",
    ai_cooldown:"انتظر 20 ثانية بين محاولات التفسير، ثم جهّز معاينة جديدة.", auth_required:"انتهت جلسة الدخول. ادخل مجددًا برمز التجربة.", demo_unavailable:"تعذر الوصول إلى عدّاد الاستخدام. تم إيقاف التفسير احترازيًا؛ حاول لاحقًا.",
    brand:"شاهد", badge:"دليل محلي · تفسير Nemotron اختياري", lead:"من سجلّ الموقع إلى ملاحظة يمكنك التحقق من دليلها.",
    intro:"استخرج الملاحظات محليًا، ثم اطلب شرحًا بالعربية أو الإنجليزية من NVIDIA Nemotron عبر Nebius Token Factory.",
    workflow:"١. حلّل محليًا  ←  ٢. راجع البيانات  ←  ٣. اطلب التفسير  ←  ٤. تحقق من الدليل",
    inputTitle:"ابدأ بسجل تجريبي", normal:"نشاط طبيعي", loginSample:"محاولات دخول متكررة", sensitiveSample:"طلبات لمسارات حساسة", burstSample:"زيارات مشروعة كثيفة · عينة",
    fileLabel:"أو اختر ملف Nginx بصيغة .log أو .txt — حتى 100 KB", chooseFile:"اختر ملفًا", noFile:"لم يُختر ملف", logLabel:"محتوى السجل",
    localPrivacy:"العينات مصطنعة. التحليل المحلي لا يتصل بالنموذج. لا يُحفظ السجل على القرص بواسطة التطبيق.", analyze:"حلّل السجل محليًا",
    resultsTitle:"الملاحظات المحلية والأدلة", localOrigin:"تستخرج القواعد هذه الملاحظات من السجل، وليست نصًا أنشأه النموذج.",
    requests:"الطلبات", sources:"المصادر", invalid:"أسطر غير مقروءة", observations:"الملاحظات", supporting:"عدد الطلبات الداعمة", showEvidence:"عرض الدليل",
    none:"لم تتجاوز البيانات عتبات القواعد الحالية. هذا لا يثبت خلو الموقع من المشكلات.", events:"الأحداث المقروءة",
    optional:"اختياري · استدعاء حقيقي", aiTitle:"اشرح الملاحظات باستخدام Nemotron", aiIntro:"راجع البيانات التي ستُرسل أولًا. يُكتب التفسير بلغة الواجهة الحالية؛ لا يؤدي تغيير اللغة إلى استدعاء تلقائي.",
    preview:"راجع البيانات قبل الإرسال", payloadTitle:"بيانات السجل المُهيّأة للإرسال (JSON)",
    previewNotice:"تُستبدل عناوين IP بمعرّفات وتُحذف معاملات URL والإحالات وUser-Agent. تبقى الأوقات والمسارات وقد تحمل معلومات حساسة. تُرسل البيانات المعروضة مع تعليمات تفسير ثابتة؛ المعاينة نفسها لا تستدعي النموذج.",
    consent:"راجعت البيانات المعروضة وأوافق على إرسالها إلى Nebius Token Factory لتفسيرها باستخدام Nemotron.",
    interpret:"أرسل وفسّر بالعربية", costNotice:"طلب واحد لكل ضغطة، بحد أقصى 4096 توكن إخراج. يستهلك الرصيد ولا توجد إعادة تلقائية. صلاحية المعاينة 10 دقائق ولمرة واحدة.",
    aiGenerated:"تفسير مولّد بالذكاء الاصطناعي — راجعه", refsChecked:"تم التحقق من وجود المراجع وارتباطها بالملاحظات؛ لم تُثبت صحة التفسير آليًا.", localScope:"بيان نطاق من القواعد المحلية",
    alternatives:"تفسيرات بديلة", missing:"معلومات ناقصة", checks:"خطوات تحقق مقترحة للمراجعة فقط", limitations:"حدود التفسير", tokens:"التوكنات", latency:"الوقت",
    scope:"هذه عتبات تجريبية لصيغة Nginx محددة. السجل والتفسير لا يؤكدان وقوع اختراق أو سلامة الموقع. قد تبقى قيم حساسة في المسارات.",
    footer:"شاهد · نموذج أولي محلي · NVIDIA Nemotron × Nebius Token Factory · العربية / English",
    sampleLoaded:"تم تحميل عينة مصطنعة. اضغط حلّل السجل محليًا.", fileLoaded:"تمت قراءة الملف في المتصفح. اضغط زر التحليل للمتابعة.",
    analyzing:"جارٍ التحليل محليًا…", analyzed:"اكتمل التحليل المحلي. لم يُستدعَ نموذج ذكاء اصطناعي.", changed:"تغيّر السجل؛ حلّله مجددًا قبل طلب التفسير.",
    languageChanged:"تم تغيير اللغة. أي تفسير جديد سيستخدم هذه اللغة؛ لم يُرسل طلب للنموذج.", preparing:"جارٍ تجهيز المعاينة محليًا…", previewReady:"المعاينة جاهزة؛ راجعها ثم فعّل الموافقة للإرسال.",
    interpreting:"جارٍ انتظار تفسير Nemotron… قد يستغرق الطلب نحو دقيقة. لا تُغلق الصفحة.", interpreted:"وصل تفسير Nemotron وتم فحص مراجعه.",
    invalid_input:"تعذر التحليل. استخدم سجل Nginx صالحًا ضمن حد 100 KB.", network_error:"تعذر الاتصال بالخادم. تأكد أنه يعمل؛ إذا سبق إرسال الطلب فراجع الاستخدام قبل تكراره.",
    ai_input_limit:"لتفسير الذكاء الاصطناعي استخدم مقطعًا أصغر: حتى 80 حدثًا و8 ملاحظات و32 KB من البيانات المُهيّأة. التحليل المحلي ما زال متاحًا.",
    ai_not_configured:"راجع مفتاح Nebius واسم Nemotron في ملف .env على الخادم.", consent_required:"راجع البيانات وفعّل خانة الموافقة أولًا.",
    preview_expired:"المعاينة تغيّرت أو انتهت أو استُخدمت. اضغط راجع البيانات للحصول على معاينة جديدة.", ai_busy:"يوجد طلب قيد التنفيذ. انتظر انتهائه قبل المحاولة.",
    invalid_ai_response:"لم يطابق الرد البنية المطلوبة؛ لم نعرضه كتفسير صالح. قد استُهلك رصيد الطلب. لا توجد إعادة تلقائية.",
    invalid_ai_references:"رُفض رد النموذج لأن مراجعه غير صالحة أو لا تخص الملاحظة. لم نعرضه كتفسير موثوق؛ قد استُهلك رصيد الطلب.",
    incomplete_ai_response:"لم يُرجع النموذج تفسيرًا مكتملًا. قد وصل إلى حد الإخراج أو رفض الطلب. راجع الاستخدام قبل طلب جديد.",
    unexpected_ai_model:"اسم النموذج في الرد لا يطابق Nemotron المختار؛ رُفض الرد.",
    unexpected_ai_language:"احتوى الرد على مزج لغوي غير متوقع؛ لم نعرضه كتفسير صالح. قد استُهلك رصيد الطلب واحتُسبت المحاولة. لا توجد إعادة تلقائية؛ راجع النتيجة مع صاحب المشروع.", provider_error:"تعذر إتمام طلب Nebius. راجع الحساب والخدمة؛ لا توجد إعادة تلقائية.",
    provider_400:"رفض Nebius إعداد الطلب. راجع توافق النموذج مع JSON Schema.", provider_401:"لم يقبل Nebius المفتاح؛ راجع ملف .env والمشروع.",
    provider_402:"الرصيد أو الفوترة غير جاهزين. راجع رصيد Token Factory.", provider_403:"الوصول مرفوض. راجع صلاحيات المشروع وإتاحة النموذج.", provider_404:"راجع معرّف النموذج ورابط Token Factory.",
    provider_429:"وصل الحساب إلى حد الاستخدام. راجع الحدود قبل طلب جديد.", provider_timeout:"انتهت مهلة الانتظار. قد وصل الطلب؛ راجع الاستخدام قبل تكراره.", origin_rejected:"افتح التطبيق من عنوانه المحلي مباشرة.",
    rules:{repeated_login_rejection:["طلبات دخول مرفوضة متكررة خلال دقيقة","قد تستحق مراجعة سجل المصادقة. استجابات 401 و403 وحدها لا تثبت تخمين كلمات المرور أو نجاح اختراق."], sensitive_paths:["طلبات لمسارات حساسة","تحقق من غرض الطلبات وإعداد الخادم؛ طلب المسار لا يثبت أن الملف موجود أو أن بيانات تسربت."], request_burst:["كثافة طلبات خلال دقيقة","ملاحظة عن المعدل فقط؛ قد تمثل استخدامًا مشروعًا أو مصدرًا مشتركًا، ولا تكفي لإثبات هجوم."]}
  },
  en: {
    logout:"Sign out", demoPrivacy:"Logs are sent to the Shahid server for rule-based analysis. The application does not save their contents, but retains usage counters and sign-in sessions. Start with synthetic samples.",
    demoUsage:"Attempts remaining: session {session} · site today {daily} · site total {total}. Daily reset is UTC. Failed provider attempts count too.",
    ai_disabled:"Interpretation is temporarily paused by the owner. Rule-based analysis remains available.", quota_exhausted:"The demo attempt quota has been reached. Rule-based analysis remains available; contact the owner if more attempts are needed.",
    ai_cooldown:"Wait 20 seconds between interpretation attempts, then prepare a new preview.", auth_required:"Your sign-in session has expired. Sign in again with the demo access code.", demo_unavailable:"Usage accounting is temporarily unavailable. Interpretation has been blocked as a precaution; try later.",
    brand:"Shahid", badge:"Local evidence · Optional Nemotron interpretation", lead:"From access logs to observations you can verify.",
    intro:"Find observations locally, then request an Arabic or English explanation from NVIDIA Nemotron through Nebius Token Factory.",
    workflow:"1. Analyze locally  →  2. Review data  →  3. Request interpretation  →  4. Check evidence",
    inputTitle:"Start with a sample log", normal:"Normal activity", loginSample:"Repeated login rejections", sensitiveSample:"Sensitive-path requests", burstSample:"Legitimate traffic burst · sample",
    fileLabel:"Or choose a Nginx .log or .txt file — up to 100 KB", chooseFile:"Choose file", noFile:"No file selected", logLabel:"Log contents",
    localPrivacy:"Samples are synthetic. Local analysis does not contact the model. The application does not save log contents to disk.", analyze:"Analyze locally",
    resultsTitle:"Local observations and evidence", localOrigin:"These observations come from local rules, independently of the model's prose.",
    requests:"Requests", sources:"Sources", invalid:"Unread lines", observations:"Observations", supporting:"Supporting requests", showEvidence:"Show evidence",
    none:"No configured rule threshold was crossed. This does not establish that the site is safe.", events:"Parsed events",
    optional:"Optional · Live inference", aiTitle:"Explain observations with Nemotron", aiIntro:"Review the data first. New interpretations use the current interface language; switching languages never calls the model automatically.",
    preview:"Review data before sending", payloadTitle:"Prepared log data to send (JSON)",
    previewNotice:"IPs become aliases; URL queries, referrers and User-Agent are removed. Times and paths remain and may contain sensitive information. The displayed data is sent with fixed interpretation instructions. Previewing does not call the model.",
    consent:"I reviewed the displayed data and agree to send it to Nebius Token Factory for interpretation by Nemotron.",
    interpret:"Send and explain in English", costNotice:"One request per click, up to 4096 output tokens. Uses credits, with no automatic retries. Preview expires after 10 minutes and can be used once.",
    aiGenerated:"AI-generated interpretation — review required", refsChecked:"References exist and belong to their observations. The truth of the model's prose has not been verified.", localScope:"Scope statement from local rules",
    alternatives:"Alternative explanations", missing:"Missing information", checks:"Suggested manual verification steps", limitations:"Interpretation limits", tokens:"Tokens", latency:"Time",
    scope:"Prototype thresholds for a limited Nginx format. Neither logs nor interpretation confirm compromise or site safety. Paths may still contain sensitive values.",
    footer:"Shahid · Local prototype · NVIDIA Nemotron × Nebius Token Factory · العربية / English",
    sampleLoaded:"Synthetic sample loaded. Click Analyze locally.", fileLoaded:"File read in your browser. Click Analyze locally to continue.",
    analyzing:"Analyzing locally…", analyzed:"Local analysis complete. No AI model was called.", changed:"Log changed. Analyze it again before requesting interpretation.",
    languageChanged:"Language changed. New interpretations will use this language; no model request was sent.", preparing:"Preparing preview locally…", previewReady:"Preview ready. Review it, then check the consent box to send.",
    interpreting:"Waiting for Nemotron… The request may take about a minute. Keep this page open.", interpreted:"Nemotron interpretation received; references checked.",
    invalid_input:"Analysis failed. Use a valid Nginx log within the 100 KB limit.", network_error:"Cannot reach the server. Check that it is running. If a request was sent, check usage before repeating it.",
    ai_input_limit:"For AI interpretation, use a smaller excerpt: up to 80 events, 8 observations and 32 KB of prepared data. Local analysis remains available.",
    ai_not_configured:"Check the Nebius key and Nemotron model ID in the server's .env file.", consent_required:"Review the data and check the consent box first.",
    preview_expired:"Preview changed, expired or was already used. Click Review data to prepare a new one.", ai_busy:"Another request is running. Wait for it to finish.",
    invalid_ai_response:"The response did not match the required structure and was not displayed as a valid interpretation. Credits may have been used. No automatic retry was sent.",
    invalid_ai_references:"The model returned invalid references or linked an observation to unrelated evidence. The response was rejected; credits may have been used.",
    incomplete_ai_response:"The model did not return a complete interpretation. It may have reached its output limit or refused. Check usage before a new request.",
    unexpected_ai_model:"The response model did not match the selected Nemotron model. Response rejected.",
    unexpected_ai_language:"Unexpected language mixing was detected and the interpretation was not displayed. Credits may have been used and the attempt counts. No automatic retry was sent; contact the owner for review.", provider_error:"Nebius request failed. Check your account and service status. No automatic retry was sent.",
    provider_400:"Nebius rejected the request settings. Check JSON Schema support for this model.", provider_401:"Nebius rejected the key. Check .env and the selected project.",
    provider_402:"Credits or billing are not ready. Check your Token Factory balance.", provider_403:"Access denied. Check project permissions and model access.", provider_404:"Check the exact model ID and Token Factory endpoint.",
    provider_429:"Account rate or quota limit reached. Check limits before a new request.", provider_timeout:"Request timed out but may have reached Nebius. Check usage before repeating it.", origin_rejected:"Open the application directly at its localhost address.",
    rules:{repeated_login_rejection:["Repeated rejected login requests within a minute","Review authentication logs. HTTP 401/403 alone do not prove password guessing or a successful compromise."], sensitive_paths:["Requests to sensitive paths","Check request intent and server configuration. A request does not prove that a file exists or that data leaked."], request_burst:["Request burst within a minute","This is a rate observation. Legitimate activity or a shared source may explain it; this does not establish an attack."]}
  }
};
let lang = "ar";
try { if(localStorage.getItem("shahid-language") === "en") lang = "en"; } catch {}
let report = null, preview = null, ai = null, busy = false, fileName = "", demo = null;
const t = key => strings[lang][key] || strings[lang].provider_error;
const say = (id, key) => { $(id).textContent = t(key); };
const validText = () => $("logtext").value.trim() && new TextEncoder().encode($("logtext").value).length <= 100000;
function clearAI() { preview = null; ai = null; $("preview-panel").hidden = true; $("ai-result").hidden = true; $("ai-result").replaceChildren(); $("payload").textContent = ""; $("consent").checked = false; $("ai-message").textContent = ""; $("interpret").disabled = true; }
function invalidate() { report = null; clearAI(); $("results").hidden = true; }
function setBusy(value) {
  busy = value;
  document.querySelectorAll("button,input,textarea").forEach(el => { el.disabled = value; });
  $("interpret").disabled = value || !preview || !$("consent").checked;
}
async function api(url, payload) {
  let response;
  try { response = await fetch(url, payload === undefined ? {} : {method:"POST", headers:{"Content-Type":"application/json"}, body:JSON.stringify(payload)}); }
  catch { throw new Error("network_error"); }
  let data;
  try { data = await response.json(); } catch { throw new Error("network_error"); }
  if(!response.ok) {
    if(response.status === 401 && data.detail?.code === "auth_required") location.replace("/login");
    const error = new Error(data.detail?.code || (response.status === 422 || response.status === 413 ? "invalid_input" : "provider_error"));
    error.usage = data.detail?.usage; throw error;
  }
  return data;
}
function renderDemo() {
  if(demo?.mode !== "hosted") return;
  $("demo-panel").hidden = false;
  $("demo-usage").textContent = t("demoUsage").replace("{session}", demo.session_remaining).replace("{daily}", demo.daily_remaining).replace("{total}", demo.total_remaining)
    + (demo.enabled ? "" : ` ${t("ai_disabled")}`);
  document.querySelector('[data-i18n="localPrivacy"]').textContent = t("demoPrivacy");
  document.querySelector('[data-i18n="footer"]').textContent = lang === "ar" ? "شاهد · تجربة الحكّام · NVIDIA Nemotron × Nebius Token Factory" : "Shahid · Judging demo · NVIDIA Nemotron × Nebius Token Factory";
}
async function refreshDemo() {
  try { demo = await api("/api/demo"); renderDemo(); } catch(error) { say("ai-message", error.message); }
}
$("logout").addEventListener("click", async () => {
  try { await api("/api/auth/logout", {}); location.replace("/login"); }
  catch(error) { say("ai-message", error.message); }
});
function evidenceButtons(ids, parent) {
  const buttons = node("div", "", "evidence-links");
  ids.forEach(id => {
    const button = node("button", id, "evidence-link"); button.type = "button";
    button.setAttribute("aria-label", `${t("showEvidence")} ${id}`);
    button.addEventListener("click", () => {
      document.querySelectorAll(".highlight").forEach(el => el.classList.remove("highlight"));
      const row = $(`evidence-${id}`); row?.classList.add("highlight");
      row?.scrollIntoView({behavior:"smooth", block:"center"}); row?.focus({preventScroll:true});
    }); buttons.append(button);
  }); parent.append(buttons);
}
function renderReport() {
  if(!report) return;
  $("stats").replaceChildren(); $("findings").replaceChildren(); $("evidence").replaceChildren();
  [["requests",report.summary.valid_requests],["sources",report.summary.unique_sources],["invalid",report.summary.invalid_lines],["observations",report.findings.length]].forEach(([key,value]) => $("stats").append(node("div",`${t(key)}: ${value}`,"stat")));
  if(!report.findings.length) $("findings").append(node("p", t("none"), "notice"));
  report.findings.forEach(finding => {
    const card = node("article", "", "finding"); const rule = strings[lang].rules[finding.kind];
    card.append(node("h3", `${finding.id} · ${rule[0]}`), node("p", `${finding.source_id} · ${t("supporting")}: ${finding.supporting_requests}`), node("p", rule[1]));
    evidenceButtons(finding.evidence_ids, card); $("findings").append(card);
  });
  report.evidence.forEach(entry => {
    const row = node("div", `${entry.id} | ${entry.time} | ${entry.source_id} | ${entry.method} ${entry.path} | ${entry.status}`, "evidence-row");
    row.id = `evidence-${entry.id}`; row.tabIndex = -1; $("evidence").append(row);
  }); $("results").hidden = false;
}
function renderAI() {
  if(!ai) return;
  const out = $("ai-result"); out.replaceChildren();
  out.append(node("h3", t("aiGenerated")), node("p", t("refsChecked"), "notice"));
  out.append(node("p", `${ai.provider} · ${ai.model} · ${ai.language.toUpperCase()} · ${t("tokens")}: ${ai.usage.total_tokens ?? "—"} · ${t("latency")}: ${(ai.latency_ms / 1000).toFixed(1)} s`, "meta"));
  if(ai.overview_source === "local_rule_scope") out.append(node("span", t("localScope"), "badge"));
  out.append(node("p", ai.interpretation.overview));
  ai.interpretation.assessments.forEach(item => {
    const card = node("article", "", "ai-card"); const finding = report.findings.find(f => f.id === item.finding_id);
    card.append(node("h3", `${item.finding_id} · ${strings[lang].rules[finding.kind][0]}`), node("p", item.explanation)); evidenceButtons(item.evidence_ids, card);
    [["alternatives",item.alternative_explanations],["missing",item.missing_information],["checks",item.verification_steps]].forEach(([key,items]) => {
      card.append(node("h4", t(key))); const list = node("ul", ""); items.forEach(text => list.append(node("li", text))); card.append(list);
    }); out.append(card);
  });
  out.append(node("h3", t("limitations"))); const limits = node("ul", ""); ai.interpretation.limitations.forEach(text => limits.append(node("li", text))); out.append(limits); out.hidden = false;
}
function applyLanguage() {
  document.documentElement.lang = lang; document.documentElement.dir = lang === "ar" ? "rtl" : "ltr";
  document.title = lang === "ar" ? "شاهد | تفسير سجلات الويب" : "Shahid | Evidence-based log triage";
  document.querySelectorAll("[data-i18n]").forEach(el => { el.textContent = t(el.dataset.i18n); });
  $("lang-ar").setAttribute("aria-pressed", String(lang === "ar")); $("lang-en").setAttribute("aria-pressed", String(lang === "en"));
  $("filename").textContent = fileName || t("noFile"); renderReport(); renderDemo();
}
["ar", "en"].forEach(value => $("lang-" + value).addEventListener("click", () => {
  if(busy || value === lang) return;
  lang = value; try { localStorage.setItem("shahid-language", lang); } catch {}
  clearAI(); applyLanguage(); say("message", "languageChanged");
}));
$("logtext").addEventListener("input", () => { invalidate(); say("message", "changed"); });
document.querySelectorAll("[data-example]").forEach(button => button.addEventListener("click", async () => {
  setBusy(true); invalidate();
  try { $("logtext").value = (await api(`/api/examples/${button.dataset.example}`)).text; $("logfile").value = ""; fileName = ""; $("filename").textContent = t("noFile"); say("message", "sampleLoaded"); }
  catch(error) { say("message", error.message); } finally { setBusy(false); }
}));
$("choose-file").addEventListener("click", () => $("logfile").click());
$("logfile").addEventListener("change", async event => {
  const file = event.target.files[0]; if(!file) return; invalidate();
  if(file.size > 100000) { $("logtext").value = ""; say("message", "invalid_input"); return; }
  setBusy(true);
  try { $("logtext").value = await file.text(); fileName = file.name; $("filename").textContent = fileName; say("message", "fileLoaded"); }
  catch { say("message", "invalid_input"); } finally { setBusy(false); }
});
$("analyze").addEventListener("click", async () => {
  invalidate(); setBusy(true); say("message", "analyzing");
  try { if(!validText()) throw new Error("invalid_input"); report = await api("/api/analyze", {text:$("logtext").value}); renderReport(); say("message", "analyzed"); }
  catch(error) { say("message", error.message); } finally { setBusy(false); }
});
$("preview").addEventListener("click", async () => {
  clearAI(); setBusy(true); say("ai-message", "preparing");
  try {
    preview = await api("/api/ai/preview", {text:$("logtext").value, language:lang});
    $("preview-meta").textContent = `${preview.provider} · ${preview.model} · ${lang.toUpperCase()}`;
    $("payload").textContent = JSON.stringify({language:preview.language, data:preview.data}, null, 2);
    $("preview-panel").hidden = false; say("ai-message", "previewReady");
  } catch(error) { say("ai-message", error.message); } finally { setBusy(false); }
});
$("consent").addEventListener("change", () => { $("interpret").disabled = busy || !preview || !$("consent").checked; });
$("interpret").addEventListener("click", async () => {
  if(busy || !preview || !$("consent").checked) return;
  const token = preview.preview_token; preview = null; setBusy(true); say("ai-message", "interpreting");
  try {
    ai = await api("/api/ai/interpret", {text:$("logtext").value, language:lang, consent:true, preview_token:token});
    renderAI(); say("ai-message", "interpreted"); $("preview-panel").hidden = true;
  } catch(error) {
    say("ai-message", error.message);
    if(Number.isInteger(error.usage?.total_tokens)) $("ai-message").textContent += ` ${t("tokens")}: ${error.usage.total_tokens}`;
  }
  finally { $("consent").checked = false; setBusy(false); await refreshDemo(); }
});
applyLanguage();
refreshDemo();

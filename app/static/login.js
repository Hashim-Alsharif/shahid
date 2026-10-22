"use strict";
const $ = id => document.getElementById(id);
const labels = {
  en: {badge:"Judging demo",brand:"Shahid",lead:"Evidence before conclusions.",title:"Enter the judging demo",
    intro:"Use the access code provided privately with the submission. No Nebius account is needed.",
    "code-label":"Access code","login-button":"Enter demo",privacy:"Start with the synthetic samples. This prototype supports manual review; it does not prove compromise or site safety.",
    login_failed:"The access code was not accepted. Check the private testing instructions.",login_limited:"Too many sign-in attempts. Wait 15 minutes before trying again.",
    network_error:"Cannot reach the demo. Try again later.",origin_rejected:"Open the demo at its original HTTPS address.",demo_unavailable:"The demo is temporarily unavailable. Please try later."},
  ar: {badge:"تجربة الحكّام",brand:"شاهد",lead:"الدليل قبل الاستنتاج.",title:"الدخول إلى تجربة شاهد",
    intro:"استخدم رمز الدخول الموجود في تعليمات الاختبار الخاصة بالمشاركة. لا تحتاج حساب Nebius.",
    "code-label":"رمز الدخول","login-button":"ادخل التجربة",privacy:"ابدأ بالعينات المصطنعة. هذا النموذج يساعد في المراجعة اليدوية، ولا يثبت الاختراق أو سلامة الموقع.",
    login_failed:"رمز الدخول غير صحيح. راجع تعليمات الاختبار الخاصة.",login_limited:"محاولات الدخول كثيرة. انتظر 15 دقيقة قبل المحاولة مجددًا.",
    network_error:"تعذر الاتصال بالتجربة. حاول لاحقًا.",origin_rejected:"افتح التجربة من عنوان HTTPS الأصلي.",demo_unavailable:"التجربة غير متاحة مؤقتًا. حاول لاحقًا."}
};
let lang = "en", lastError = "";
try { if(localStorage.getItem("shahid-language") === "ar") lang = "ar"; } catch {}
function render() {
  document.documentElement.lang = lang; document.documentElement.dir = lang === "ar" ? "rtl" : "ltr";
  ["badge","brand","lead","title","intro","code-label","login-button","privacy"].forEach(id => $(id).textContent = labels[lang][id]);
  ["ar","en"].forEach(value => $(`lang-${value}`).setAttribute("aria-pressed", String(lang === value)));
  $("login-message").textContent = lastError ? (labels[lang][lastError] || labels[lang].network_error) : "";
}
["ar","en"].forEach(value => $(`lang-${value}`).addEventListener("click", () => {
  lang = value; try { localStorage.setItem("shahid-language", lang); } catch {} render();
}));
$("login-form").addEventListener("submit", async event => {
  event.preventDefault(); $("login-button").disabled = true; lastError = "";
  const code = $("access-code").value; $("access-code").value = "";
  try {
    const response = await fetch("/api/auth/login", {method:"POST", headers:{"Content-Type":"application/json"}, body:JSON.stringify({code})});
    if(response.ok) { location.replace("/"); return; }
    const data = await response.json(); lastError = data.detail?.code || "login_failed";
  } catch { lastError = "network_error"; }
  $("login-button").disabled = false; render();
});
render();

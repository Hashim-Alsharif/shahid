# Shahid: judging instructions

**Demo:** https://shahid.rihlati.me/  
**Source:** https://github.com/Hashim-Alsharif/shahid  
**Access code:** supplied only in the private submission field. Judges do not
need a Nebius account, API key, payment, or local installation.

## Two-minute walkthrough

1. Select **English** and sign in with the private judging code.
2. Select **Repeated login rejections**, then **Analyze locally**. Expect eight
   requests, one source and one rule observation. Click **L0001** to highlight
   the original physical log line.
3. Click **Review data before sending**, inspect the prepared evidence, consent
   and click **Send and explain in English** once. This calls NVIDIA Nemotron
   through Nebius Token Factory. Preview itself does not call the model.
4. Review hypotheses, alternatives, missing information and manual verification
   steps. Follow an evidence link. Reference checks do not verify prose truth
   or establish successful intrusion. Model, tokens and latency are displayed.
5. Select **العربية** for the RTL interface and localized observations. Switching
   languages clears the old AI explanation and never calls the model automatically.
   Prepare a new preview and explicitly send if testing Arabic.
6. Optionally analyze **Legitimate traffic burst · sample** locally. Expect
   sixteen requests and a rate observation. A threshold crossing alone cannot
   establish malicious intent. No further model request is needed for this check.

## Limits and privacy

Start with synthetic samples. Logs are processed on the Shahid server; the app
does not save their contents. IPs become aliases and queries, referrers and user
agents are omitted before inference. Paths and timestamps remain and may be
sensitive: review the actual preview before consenting.

The header shows remaining attempts: five per session per UTC day, twenty per
site per UTC day, and a separate site-wide lifetime allowance. Failed provider
attempts count; no automatic retry is sent. A new session does not reset global
counters. These are attempt limits, not dollar billing caps. If evaluation is
blocked, contact the submitter through the submission channel. Local rules remain
available. The owner must monitor credits/allowances throughout judging.

The updated source rejects obvious foreign-script/word mixing, allowing known
technical terms, evidence IDs and exact input paths. This is a narrow check,
not fluency, semantic truth, or complete language detection. Languages sharing
a script cannot be distinguished. A rejected response is not silently translated
or retried, and its attempt still counts.

## Verification record: October 22, 2026

- Owner-reported Ubuntu setup: 79 passing tests and seven offline scenarios.
- Independent external probes: verified HTTPS, health 200, home 303 to sign-in,
  and API 401 without a session. The existing Rihlati home returned 200.
- Owner-reported protected flow: real Arabic Nemotron interpretation, working
  evidence links and exactly one attempt deducted. The agent did not repeat
  the protected flow without the owner's private credentials.
- The Arabic screenshot contained Cyrillic/English mixing, prompting a narrow
  rejection check. One subsequent local synthetic Arabic request passed it
  (1,827 reported tokens). This was a separate CLI request, not hosted inference
  or proof of consistently fluent output. A repeated Arabic word still needed
  human editing review; the check does not judge grammar.
- Updated source: 86 local/mocked tests and seven offline scenarios passed.
- Pending: deploy the update, verify counters across restart, and record an
  English hosted result. Do not describe these as already completed.

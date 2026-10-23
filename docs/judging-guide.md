# Shahid: judging instructions

**Demo:** https://shahid.rihlati.me/  
**Source:** https://github.com/Hashim-Alsharif/shahid  
**Access code:** supplied in the private Devpost Additional info file attachment
(`shahid-judge-access.zip`, containing `README-judges.txt`). Judges do not
need a Nebius account, API key, payment, or local installation.

## Two-minute walkthrough

1. Select **English** and sign in with the private judging code.
2. Select **Repeated login rejections**, then **Analyze locally**. Expect eight
   requests, one source and one rule observation. Click **L0001** to highlight
   its parsed event, identified by the original physical input line number.
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
available. The owner must monitor credits/allowances throughout judging. The rules
require free access without testing restrictions through December 15, 2026;
finite quotas and the remaining credit balance/expiry still need an operational review
before the final submission. Do not claim guaranteed availability from the
current successful tests alone.

The updated source rejects obvious foreign-script/word mixing, allowing known
technical terms, evidence IDs and exact input paths. This is a narrow check,
not fluency, semantic truth, or complete language detection. Languages sharing
a script cannot be distinguished. A rejected response is not silently translated
or retried, and its attempt still counts.

## Verification record: October 22–23, 2026

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
- PR #2 merged as `fceb62c66047af4b0a27c8b4db974cdd1eaff53e`. The owner reported
  `SHAHID_UPDATE_AND_COUNTER_OK` and unchanged counters across the service restart.
- The owner then reported a successful English hosted request, working evidence
  navigation and one attempt deducted. Screenshots show the English interpretation,
  highlighted event L0003, model `nvidia/nemotron-3-super-120b-a12b`, 1,746 reported
  tokens and a displayed response time of 4.7 seconds. This is one observed result,
  not a latency benchmark or proof of consistent model quality.
- October 23 owner confirmation: video https://youtu.be/VCfGjb65STs is Public,
  plays without sign-in in a private browser window, and lasts 2:52. The owner
  approved the edited clip's audio and splice.
- October 23 independent verification: YouTube oEmbed returned the Shahid title;
  public watch-page metadata reported 172 seconds, isUnlisted=false and
  isPrivate=false. HTTPS health returned 200, home redirected to /login, and the
  unauthenticated API returned 401. No model request was made for these checks.
- October 23 owner confirmation: hackathon credits received and activated.
  Remaining balance, expiry and allowances have not been independently checked.
- Pending: confirm sustained judging access and complete Devpost submission.

## Submission materials

- Public video: https://youtu.be/VCfGjb65STs.
- Private testing attachment: `shahid-judge-access.zip` in Devpost Additional info.
  It contains the code and English walkthrough. Do not copy its credential into
  public materials. Attachment upload was confirmed by the owner; its credential
  contents were not read by the agent.

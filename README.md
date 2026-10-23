# Shahid | شاهد

Evidence-based web access log triage for the Nebius × NVIDIA Global AI Hackathon.

## Current status

This is a prototype with local and authenticated hosted modes. The judging demo
is at **https://shahid.rihlati.me/** with a private judging access code. See the
[walkthrough and verification record](docs/judging-guide.md). The owner confirmed
deployment of the language-check update, counters preserved across restart,
and working hosted Arabic/English inference and evidence navigation.

**Demo video:** [Shahid walkthrough on YouTube](https://youtu.be/VCfGjb65STs)
(2:52). Public playback and video metadata were independently checked on
October 23, 2026. Judges receive the login code and English testing instructions
in the private attachment to the Devpost submission; the code is not public.

The bilingual Arabic/English FastAPI UI
parses a limited Nginx combined-log format, produces rule-based observations,
and links them to real input line IDs. Four samples are available in the UI,
with seven synthetic scenarios in the offline evaluation suite.
The web UI can optionally request structured NVIDIA Nemotron interpretation
through Nebius Token Factory after a data preview and explicit send action.
Local observations and model-generated interpretations are displayed separately.

`scripts/nebius_check.py` can validate local configuration, list the NVIDIA
Nemotron IDs returned by your Token Factory account, and make one short live
inference request. On October 22, 2026, one live request to
`nvidia/Nemotron-3_5-Lightning` returned `Shahid connection OK.` through Nebius
Token Factory (39 prompt tokens, 208 completion tokens). Local evidence is saved
under ignored `reports/nebius/smoke-last.json`. This verifies the connection,
not log interpretation quality or receipt of hackathon credits.
Mocked client tests are not evidence of live Nebius access.

The bilingual web integration was subsequently verified with Nemotron Super:
Arabic rejected-login interpretation (1,821 tokens, approximately 4.0 seconds)
and English sensitive-path interpretation (1,453 tokens, approximately 3.9 seconds).
Evidence links focused and highlighted the corresponding parsed lines. There
are 86 passing local/mocked tests. Local verification records and screenshots
are in ignored `reports/`; broader semantic quality evaluation is still pending.

## Run on Windows PowerShell

Use Python 3.12 or newer from the project directory:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8010
```

Open http://127.0.0.1:8010/ and select a synthetic sample, then the local analysis
button. Each finding has evidence links. API documentation is at `/docs`.
Stop the server with Ctrl+C. Environment activation is optional.

## Protected judging deployment

[Hosting guide](docs/hosting.md) covers the separate HTTPS judging code, eight-hour
sessions, persistent SQLite attempt counters, global daily/lifetime quotas,
session allowance, no automatic retries, and a server-shell pause switch.
Hosted inference starts disabled until explicitly enabled. Attempt quotas are
not guaranteed dollar billing limits. No judge API key is required on the hosted demo.

For the existing Ubuntu/Caddy VPS, `deploy/shahid.service` binds loopback 8011
with its own account and state directory. `deploy/Caddyfile.shahid` is an additive
site block; do not replace another application's live proxy configuration.
First verify the existing host using the read-only `scripts/vps_preflight.sh`.
Docker is an optional route for a host that already supports it.

## Try the bilingual AI workflow

1. On the hosted demo, sign in using the private judging code. For a local copy,
   configure your own `.env` as described below. The demonstrated model is
   `nvidia/nemotron-3-super-120b-a12b`; verify availability for your account.
   Never put a Nebius key in the browser.
2. Choose العربية or English at the top. Arabic uses RTL; English uses LTR.
3. Select **Repeated login rejections** and click **Analyze locally**. Expect
   eight requests and one local observation, without a model call.
4. Click **Review data before sending**. Review the displayed JSON; preparing it
   does not call Nebius. The payload has source aliases, times, methods, paths,
   statuses, summary counts, local finding IDs and their evidence IDs.
5. Check the consent box, then click **Send and explain in English** (or the
   Arabic equivalent). This sends one request through the server to Nebius,
   using the configured Nemotron model. It consumes account credits.
6. Review the explanation, alternatives, missing information and manual checks.
   Click an `L0001`-style link to focus and highlight the actual parsed line.
7. Switch language to prepare a new interpretation in that language. Previous
   AI output/consent is cleared; the local report is translated without a call.

The server requests JSON Schema output, direct answering (`enable_thinking=false`),
temperature 0.2, and at most 4,096 output tokens. Input is limited to 80 events, eight local
observations, and 32,000 bytes of prepared evidence; oversized AI input is
rejected rather than silently truncated. Local analysis retains its 100 KB limit.
Preview tickets expire after ten minutes and are single-use. If logs, language,
model or endpoint change, prepare a new preview. There is one concurrent inference
per server process, with no automatic retries. A timeout or rejected response
can still consume credits.

Generated output is schema-validated. Every local finding must appear exactly
once; its references must belong to that finding and exist in the parsed log.
Invented IDs, duplicate findings, truncated or malformed output are rejected.
These checks validate references, **not the truth or safety of generated prose**.
Interpretation remains a hypothesis for human review, never a confirmed incident.
When there are no local findings, the overview is replaced with an explicitly
labelled local rule-scope statement, rather than a model-written safety claim.
Model output may still contain language or reasoning errors; reference validation
does not detect all such errors. Manual bilingual quality evaluation remains ongoing.
The updated source rejects obvious foreign-script/word mixing, with exceptions
for known technical identifiers and exact input paths. It never silently translates
or retries the response. This is not a grammar, fluency or complete language detector.
See [Arabic walkthrough](docs/try-shahid-ar.md) for click-by-click instructions.

## Evaluate and build a test copy

```powershell
.\.venv\Scripts\python.exe -m scripts.evaluate
.\.venv\Scripts\python.exe -m scripts.build_release
```

The default evaluation is offline and makes no Nebius request. Expect seven
passing rule/evidence scenarios; that is not a detection-accuracy score. See
[evaluation notes and observed live examples](docs/evaluation.md) for scope,
manual review findings and optional single-request live evaluation commands.

The builder produces `dist/shahid-test-build.zip` and its SHA256 file from
explicit source paths. It excludes `.env`, `.git`, virtual environments and
local reports, and checks that the configured API key was not copied into source.
Extract the ZIP, open its `shahid` folder, and follow this README to set up Python
and run locally. Offline analysis/tests need no account. Live interpretation
requires a valid Nebius key/model and credits; the ZIP is not a hosted judging demo.

GitHub Actions runs tests, offline scenarios, syntax checks and bundle creation
on Python 3.12 and 3.14 without any Nebius credential or paid inference.

## Verify Token Factory

Read [the Arabic onboarding guide](docs/nebius-setup-ar.md) first. Copy
`.env.example` to `.env` only if `.env` does not already exist. The initial setup
may already have created the blank local file. Put your API key there yourself.

```powershell
.\.venv\Scripts\python.exe -m scripts.nebius_check --check-config
.\.venv\Scripts\python.exe -m scripts.nebius_check --models
```

Copy an exact `nvidia/` Nemotron ID from the account's model list into
`NEBIUS_MODEL` in `.env`, then run:

```powershell
.\.venv\Scripts\python.exe -m scripts.nebius_check --chat
```

The last command sends a short synthetic connection prompt, not any user logs.
It uses the model you selected with a maximum output budget of 1,024 tokens,
has no automatic retries, and can consume credits. A non-empty final answer
from a Nemotron model is required for PASS. It saves model, answer, usage,
and execution time under ignored `reports/nebius/smoke-last.json`; no key is
saved in that report. A model listing alone does not prove inference access.

On Linux/macOS, replace `.\.venv\Scripts\python.exe` with `.venv/bin/python`.
The default endpoint is `https://api.tokenfactory.nebius.com/v1/`; if your project
uses a regional endpoint, copy its official HTTPS `/v1/` URL from its Playground.
Do not substitute an unrelated provider for the hackathon requirement.

## Scope and data handling

- Supported input: Nginx combined access logs, up to 100,000 UTF-8 bytes of text.
- Local observations: five rejected login requests in a 60-second window,
  two sensitive-path requests, or twelve requests in a 60-second window.
- These small demonstration thresholds are not production intrusion-detection
  thresholds. A rate spike can be legitimate. Access logs alone cannot confirm
  compromise or successful authentication.
- Reports replace source IPs with per-analysis aliases and strip URL queries
  and fragments. Paths may still contain sensitive values. This is data
  minimization, not a guarantee of complete anonymization.
- Raw log text is processed in server memory and is not retained by the
  application. Previewed minimized evidence is sent to Nebius only on explicit
  submission; provider handling follows Nebius terms. Paths can retain secrets.
  The app has no shell execution or automatic blocking/remediation.
- The default local setup binds `127.0.0.1`. For a public judging deployment,
  use the [hosted configuration](docs/hosting.md): HTTPS, exact host/origin checks,
  a private demo-code gate and persistent global/session attempt limits. These
  shared-code demo controls are not individual user accounts or billing caps.
- `.env`, `.venv`, uploads, and reports are excluded from Git. Do not paste a key
  into the frontend or commit it. The client uses official HTTPS Nebius hosts,
  preserves certificate validation, and does not follow credential redirects.

## Project map

| Path | Purpose |
| --- | --- |
| `app/main.py` | Local web routes and input limits |
| `app/static/` | Arabic/English interface, preview and evidence navigation |
| `shahid/interpretation.py` | Input bounds, structured output validation, preview tickets |
| `shahid/logs.py` | Parser, local rules, evidence IDs, source aliases |
| `shahid/settings.py` | Local environment settings and endpoint validation |
| `shahid/nebius.py` | Bounded Token Factory HTTP client |
| `scripts/nebius_check.py` | Config/model-list/live-smoke CLI |
| `scripts/evaluate.py` | Offline scenarios and explicit single-case live evaluation |
| `scripts/build_release.py` | Source test bundle with credential exclusions |
| `samples/` | Synthetic documentation-range IP fixtures |
| `tests/` | Local parser, API and mocked provider tests |
| `docs/nebius-setup-ar.md` | Registration, credits, key and first-call steps |
| `docs/roadmap.md` | Remaining work and acceptance criteria |

## Next milestones

- [x] Verify live Nemotron inference through Token Factory.
- [x] Owner confirmed hackathon credits received and activated on October 23.
- [x] Connect evidence-only Nemotron interpretation to the web UI with an
  explicit send action and a preview of exactly what leaves the app.
- [x] Validate generated evidence references and distinguish observed facts
  from interpretations and missing information.
- [x] Add seven reproducible synthetic rule/evidence cases and selected live examples.
- [ ] Expand semantic quality evaluation beyond those synthetic examples.
- [x] Provide a working hosted demo URL, public repository and short video.
- [ ] Verify credit expiry and sufficient inference allowance throughout judging.
- [ ] Complete and verify the final Devpost submission.

Original code is MIT-licensed; dependencies and model usage retain their own
licenses and service terms. Running the local setup does not automatically deploy
the app or submit a hackathon entry.

## Integration references

- [Nebius structured output](https://docs.tokenfactory.nebius.com/ai-models-inference/json)
- [Nebius chat completions](https://docs.tokenfactory.nebius.com/api-reference/inference/create-chat-completion)
- [NVIDIA reasoning controls](https://docs.api.nvidia.com/nim/reference/nvidia-nemotron-3-super-120b-a12b)

Provider parameters are verified by live requests in addition to mocked tests;
model quality claims require broader evaluation than these synthetic samples.

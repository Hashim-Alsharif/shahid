# Hackathon submission preparation

Status: source/test-build preparation. A hosted judging demo, public demo video
and final Devpost submission are still pending. Do not submit placeholder links.

## Project overview

Name: **Shahid — Evidence-linked Log Triage**

Elevator pitch:

Turn web access logs into reviewable observations, then use NVIDIA Nemotron on
Nebius Token Factory to explain possibilities and link them to the original evidence.

Track: **Best Apps and Agents**.

## Project story draft

### Inspiration

Small teams often have access logs but limited time to interpret them. A fluent
AI explanation is not enough if the reader cannot verify what it refers to.
Shahid helps a solo developer move from log entries to a focused manual review.

### What it does

Shahid parses a limited Nginx combined-log format, assigns evidence IDs based on
physical input line numbers, and applies three local observation rules. It can
flag repeated rejected logins, sensitive-path requests and request bursts.

The developer reviews a minimized evidence preview before sending it to NVIDIA
Nemotron through Nebius Token Factory. The model explains possibilities,
alternative explanations, missing information and suggested manual checks.
Each explanation links to parsed evidence. Arabic and English interfaces and
generation are supported, with RTL/LTR layouts.

The server rejects malformed or incomplete output, invented evidence IDs and
references belonging to unrelated observations. These checks verify structure
and reference relationships, not the truth of generated prose. Access logs do
not establish intent, successful authentication, compromise or site safety.

### How I built it

Python, FastAPI, HTTPX and Pydantic power the backend. The interface uses HTML,
CSS and JavaScript. A local parser and deterministic rules produce observations
independently of the model. IP addresses become source aliases and URL queries,
referrers and user agents are omitted from the model input. Paths and timestamps
remain visible in the preview and can still contain sensitive values.

The backend makes real runtime calls to Nebius Token Factory's chat completions
API using `nvidia/nemotron-3-super-120b-a12b`. It requests JSON Schema output in
direct-answer mode and validates references before rendering. Token usage,
model identity and latency are displayed. Requests are bounded and never retried
automatically. The application does not execute model-written commands or
automatically block traffic.

### Challenges and lessons

An initial reasoning-enabled request did not return a complete answer within
the output budget. Direct-answer mode made the short structured task practical.
I compared Arabic samples from multiple Nemotron models and selected Super for
the bilingual interface. Model text still needs human review.

A no-finding model overview was broader than the local checks justified. The
application now shows an explicitly labelled local scope statement for that
case. A legitimate burst fixture demonstrates why a rate observation must not
be treated as a confirmed attack.

### What's next

Expand evaluation beyond synthetic cases, improve language consistency and
add authenticated deployment with spending controls for a judging demo.

## Built with

Python, FastAPI, HTTPX, Pydantic, pytest, JavaScript, HTML, CSS, NVIDIA Nemotron,
Nebius Token Factory, JSON Schema, GitHub Actions.

## Required links and materials

- Public repository: https://github.com/Hashim-Alsharif/shahid (verify uploaded source and license before submission).
- Working demo/test-build URL: **pending**. Localhost is not a public judging URL.
- Public YouTube video under three minutes: **pending**.
- English testing instructions: README plus the final hosted-demo access instructions.
- Nebius/NVIDIA feedback: include real observations from evaluation, not assumed benefits.

## Official requirements checked October 22, 2026

[Rules](https://nebiusglobalaihackathon.devpost.com/rules): runtime use of Token
Factory or AI Cloud plus at least one NVIDIA open model; public licensed source
with setup instructions; working demo/hosted app/test-build URL; public YouTube
video under three minutes. Materials must be English or have English translations.
Testing access must be free to judges through the end of judging, December 15,
2026. Submission deadline: October 30, 2026, 20:00 Asia/Riyadh.

Preserve a submitted version and its evaluation evidence so judges can reproduce
the demonstrated behavior. Publishing a repository is not a Devpost submission.

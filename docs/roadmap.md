# Shahid implementation milestones

## Foundation delivered

- Independent project/environment and MIT license.
- Local Nginx parser, three small observation rules, actual input line evidence.
- Source IP aliases and query removal; remaining path privacy limits stated.
- Three synthetic fixtures, Arabic/English UI, and a bounded Token Factory smoke CLI.
- Local/mocked tests kept separate from live inference evidence.
- Live Token Factory smoke request verified on October 22, 2026 with
  `nvidia/Nemotron-3_5-Lightning`; response: `Shahid connection OK.` (247 tokens).

## Interpretation integration delivered

- Explicit data preview and consent, Arabic/English generation, RTL/LTR UI.
- Bounded JSON Schema output and server-side evidence/finding reference checks.
- Local observations separated from AI hypotheses; prose truth is not verified.
- Single-use ten-minute preview tickets, single concurrent request per process,
  safe localized errors and no automatic retries.
- Live Arabic and English UI requests verified with Lightning. An initial
  incomplete request was rejected; direct-answer mode resolved that failure.
- Super was selected for the bilingual UI after comparing Arabic samples from
  Lightning, Super and Ultra. Language quality still requires human review.

## Remaining

1. Confirm credit amount/expiry and allowances cover the judging period; the
   owner confirmed receiving and activating hackathon credits on October 23.
2. Expand manual quality evaluation beyond the seven synthetic scenarios and
   selected recorded live examples in docs/evaluation.md.
3. Confirm enough funded inference and allowance for judging through December 15;
   current finite quotas alone do not establish unrestricted testing access.
4. Complete the Devpost draft, review the final fields and submit. The owner
   confirmed https://youtu.be/VCfGjb65STs is Public and plays in a private window
   with a duration of 2:52.

## Hosted acceptance and video preparation

- Owner confirmed the PR #2 deployment marker and counters preserved across restart.
- Owner confirmed English hosted interpretation, working evidence navigation and
  exactly one additional attempt; screenshots display the real provider/model result.
- English narration, an optional Arabic translation, recording storyboard and
  private judging-field template are prepared. The owner recorded two takes;
  an edited 172.137-second review copy was exported, and the owner approved the
  sound/splice and confirmed its public YouTube upload on October 23.

## Submission preparation delivered

- Seven offline synthetic rule/evidence scenarios, including a benign burst,
  sparse rejected logins, malformed lines and an instruction-like path.
- Selected actual live normal/burst/instruction-path outputs, with manual review
  notes and explicit limits on what those examples establish.
- Labelled local scope summary for zero-finding results.
- Source ZIP builder excluding credentials/local reports, SHA256 and source manifest.
- GitHub Actions configuration for offline verification; check its actual run
  before describing CI as passed. Test bundle instructions and English submission draft.

## Keep the first version small

Hosted preparation now includes a shared judging-code gate, durable global
attempt quotas, per-session allowance, and operator pause. These are not
per-person identity or guaranteed dollar billing limits. HTTPS is deployed and
the owner reported real hosted inference; see `hosting.md` and `judging-guide.md`.

One log format, one web page, synthetic examples, and report review. No automatic
firewall changes, shell commands, log-agent deployment, persistent customer data,
or claim of confirmed compromise from access logs alone.

Track: Best Apps and Agents. The NVIDIA model must be called through Nebius at
runtime (or run on Nebius AI Cloud); local rules and a prepared configuration
alone do not meet that requirement. The protected demo is at https://shahid.rihlati.me/.

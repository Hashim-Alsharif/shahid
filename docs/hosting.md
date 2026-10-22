# Judging demo: access and inference quotas

## Status

Hosted-mode safeguards are implemented and covered by offline/mocked tests.
The public judging site is **not deployed yet**. Linux service/container files
are prepared; they still need validation on the actual target. No IONOS service,
DNS record, existing Rihlati data, or live Caddy configuration was changed.

The owner's existing IONOS VPS is Ubuntu 24.04, 2 vCPU, 4 GB RAM, 120 GB storage.
Local Rihlati deployment documentation records Caddy/systemd and loopback 8080.
Confirm live resource use and configuration before relying on that inventory.
Shahid inference runs on Nebius, not on a local GPU.

## Access model

- HTTPS origin must be configured exactly. Only that Host is accepted.
- A shared private judging access code is stored as a salted scrypt hash.
  This is a small demo gate, not individual user accounts or identity verification.
- Random sessions expire after eight hours. Cookies are Secure, HttpOnly,
  SameSite=Strict and host-only with a `__Host-` prefix. Session tokens are hashed
  in SQLite; the raw access code is not retained. Logout revokes its session.
  Changing the configured access-code hash invalidates previous cookies.
- Every hosted state-changing request requires the exact same Origin, including
  sign-in. There is no cross-origin API or alternate bearer-key inference route.
- Sign-in attempts are capped globally at 30 per 15 minutes, persisted across
  restarts. This deliberately avoids trusting arbitrary forwarded IP headers.
  It can temporarily block legitimate sign-in too; it is not DDoS protection.
- OpenAPI/docs are disabled in hosted mode. Static assets, sign-in and a minimal
  `/health` are public; data and inference APIs require the session.
- Previews are single-use, ten minutes, tied to session/data/language/model.
- CSP, no-store, no-referrer and anti-framing headers are set. Hosted HSTS is
  enabled only for the configured hostname; it does not cover sibling sites.

## Attempt quotas and emergency pause

Defaults: **20 site-wide attempts per UTC day, 120 over the database lifetime,
five per session per UTC day, and 20 seconds between site-wide attempts**.
Daily counters reset at 00:00 UTC (03:00 Saudi time). Lifetime counters do not.
New login sessions can obtain a new session allowance; the global daily and
lifetime ceilings remain authoritative. This is not a per-person quota.

An atomic SQLite reservation happens before contacting Nebius. Errors, timeouts
and rejected model outputs still consume the reserved attempt; no automatic
retry/refund occurs. Unknown provider token usage remains unknown. Only bounded
reported token counts are retained alongside timestamps and session identifiers.
No source logs, prompts, model answers or access codes are stored in that ledger.
The hosting platform/reverse proxy may separately retain connection metadata.

The same persistent database must survive every restart/deploy. Never delete it
or mount ephemeral storage: a new database means new counters. SQLite failure
blocks inference. One worker and one instance are required. A persisted three-minute
lease additionally blocks immediate retry after process failure; the process lock
remains the active concurrency gate. Do not scale this design horizontally.

Input is capped at 100 KB of logs, 80 events/eight findings/32 KB of prepared
evidence and 4096 output tokens. The HTTP body is bounded before JSON parsing.
These are request-count/data limits, **not a guaranteed dollar spending cap**.
Other clients using the same Nebius project/key are outside this ledger. Use a
separate Nebius key/project for the demo where available, review provider billing,
and keep paid inference off until the demo quota and available credits are checked.

Server-shell controls (no public admin endpoint):

```sh
cd /opt/shahid
sudo .venv/bin/python -m scripts.demo_admin status --env-file /etc/shahid/demo.env
sudo .venv/bin/python -m scripts.demo_admin pause --env-file /etc/shahid/demo.env
sudo .venv/bin/python -m scripts.demo_admin resume --env-file /etc/shahid/demo.env
```

Do not put secrets into shell history. The operator commands read the root-owned
environment file without printing it. `pause` persists in the database and stops
new reservations; it does not cancel a request already running. `resume` does
not override `SHAHID_AI_ENABLED=false`. The code generator below has no network
request and prompts without echoing a manually chosen code.

```sh
/opt/shahid/.venv/bin/python -m scripts.demo_admin hash-code
```

## IONOS deployment sequence: shared VPS with Rihlati

Proceed in stages; do not paste a broad installation script into the live server.

1. Open an existing SSH session or IONOS console. Run `scripts/vps_preflight.sh`
   after reviewing it, or collect `free -h`, `df -h /`, `uptime`, `ss -ltn`,
   `systemctl is-active caddy rihlati` and `python3 --version` manually. Verify
   memory headroom and that 8011 is free. Read existing Caddy configuration
   privately and back it up before changes. Never share credentials/config secrets.
2. Create a separate system account `shahid` and deployment directory `/opt/shahid`.
   Code/venv should be owned by the deployment administrator, not writable by the
   running service. Do not use `/opt/rihlati`, its environment file or its database.
   Clone the reviewed Shahid commit, create its own Python 3.12+ venv, and install
   `requirements-lock.txt`. Run offline tests with an isolated writable temp folder.
3. Put the completed `deploy/demo.env.example` at `/etc/shahid/demo.env`, owned by
   root and mode 600. Enter the Nebius key in a private editor. Generate/save the
   private judging code and copy only its hash to the environment file. Do not
   reuse a Rihlati user password or put the judging code in GitHub/the public story.
   Keep `SHAHID_AI_ENABLED=false` for the first deployment.
4. Validate `deploy/shahid.service` using `systemd-analyze verify`, then install it
   as a NEW service. Its `StateDirectory` owns `/var/lib/shahid`, isolated from
   Rihlati. It binds `127.0.0.1:8011`, has MemoryMax=512M and CPUQuota=50%, and
   starts a single Uvicorn worker. These limits still require live resource checks.
5. Verify `/health` with the intended Host header locally. In DNS add only the
   new `shahid` A record pointing to this confirmed VPS. Add AAAA only if this VPS's
   IPv6 is configured and reachable. Do not alter apex/www/MX/TXT Rihlati records.
6. Append the separate `deploy/Caddyfile.shahid` site block after reviewing current
   `/etc/caddy/Caddyfile`; do not replace existing sites. Validate the combined
   config before a Caddy reload. Caddy obtains TLS for the new hostname. No need
   to expose 8011 in the firewall or install a second web proxy.
7. Verify externally: valid TLS, unauthenticated redirect, API 401, working Arabic/
   English login, cookie flags, logout, local analysis, no AI on preview, rejected
   cross-origin POST and correct remaining counters. Check Rihlati still works.
8. Only after those checks, confirm available Nebius balance, enable AI in the
   private server file and restart **only `shahid`**. Test one synthetic live
   request, inspect usage and counter change, then reload/restart and confirm the
   counter persists. Never describe a mocked test as live hosted inference.
9. Provide judges the HTTPS URL and private access code in Devpost's private
   testing instructions. Keep access free/available through judging; monitor
   remaining attempts and credits so quotas do not unexpectedly stop evaluation.
   Keep a secure off-server SQLite backup using SQLite's backup API. Backups and
   restored counters must not be made public or casually reset to older totals.

On rollback, stop/remove only Shahid's newly added service/site; preserve its
ledger and do not stop Rihlati. Do not use a blanket Caddy replacement or reset
the firewall. Test Rihlati again after any proxy reload.

## Optional container

`Dockerfile` and `compose.yaml` offer a separate single-instance route for an
existing Docker host. Copy the blank example to `.env.hosted` and fill it privately;
the compose file overrides hosted mode and database path. It binds loopback 8011,
uses a persistent named volume, non-root UID 10001 and read-only container root.
The Docker build context excludes local `.env`, reports, releases and private data.
The image/runtime have not been built on this Windows environment (Docker absent).
Do not run `docker compose down -v`, which would delete the quota ledger.

## Private judging instructions template (finish after deployment)

URL: **pending deployment**. Access code: **provide in private field only**.

1. Open the HTTPS URL, choose English and sign in using the supplied code.
2. Select Repeated login rejections, then Analyze locally. Review the rule finding
   and follow an evidence link to its original line.
3. Select Review data before sending, review the prepared data, consent and send.
   NVIDIA Nemotron runs through Nebius Token Factory; no judge API key is needed.
4. Read hypotheses, alternatives, missing information and verification steps.
   Reference checks do not establish the truth of the model's prose.
5. Switch to Arabic to see RTL/localized rules. A new interpretation requires a
   new preview and send; changing language itself does not call the provider.
6. The header shows remaining attempts. If inference is unavailable, contact the
   submitter; local rule-based analysis still works. No automatic repair is run.

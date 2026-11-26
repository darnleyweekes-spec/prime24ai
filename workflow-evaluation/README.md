# Prime24AI AI Workflow Evaluation Dashboard

A working Python/Streamlit portfolio project for processing fictional home-service inquiries, reviewing drafts, and testing extraction and failure handling. Includes a local HTTP backend, SQLite audit/history, a 30-case labeled benchmark, offline fixtures, and one OpenAI API integration. Nothing sends customer messages or changes external business systems.

This is a new execution/evaluation layer inside the existing Prime24AI repository. The source website has assessment intake and draft-review concepts, but no AI lead backend in the supplied repository. See [source review](docs/source-review.md) for exact source paths and commit. Original website files are unchanged.

## Setup (no Docker)

Python 3.11+; verified here with Python 3.12. Run all commands from `workflow-evaluation/`:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.lock
python -m pytest -q
python -m lead_eval --mode fixture --output reports/fixture-evaluation.json
python -m streamlit run app.py --server.address=127.0.0.1
```

On Windows activate with `.venv\Scripts\Activate.ps1` in PowerShell. Alternatively use `python -m pip install -e ".[test]"` for compatible dependency ranges instead of the exact tested lock. Source checkout is required for data and documentation; this is not a standalone wheel distribution.

Open the Streamlit URL printed by the command. The dashboard loads persisted runs from SQLite. On a fresh checkout run the fixture CLI or click **Run 30-case fixture evaluation**. Use **Process inquiry**, choose a sample, then use **Staff approval** to review and approve it. The approval checkbox and staff identifier are mandatory. Reprocessing a matching inquiry in the same mode returns a duplicate. An unknown fixture produces an explicit `fixture_not_found` error; fixture mode supports the 20 curated inquiry texts, not arbitrary text generation.

## HTTP AI lead backend

In another terminal, with the same virtual environment and working directory:

```bash
python -m lead_eval.server --port 8765
curl http://127.0.0.1:8765/health
curl -X POST http://127.0.0.1:8765/api/leads \
  -H 'Content-Type: application/json' --data-binary @data/example-request.json
```

Use the returned ID with these routes:

| Method | Route | Behavior |
|---|---|---|
| GET | `/health` | Readiness and live-key presence; no secret values |
| POST | `/api/leads` | Extract fields, draft, persist; `mode` is fixture by default or live |
| GET | `/api/leads/<id>` | Retrieve persisted state, draft and attempt log |
| POST | `/api/leads/<id>/approve` | Body `{"staff":"Demo reviewer","confirmed":true}`; approves only a pending draft |

Lead request: `{"inquiry":"fictional inquiry text","mode":"fixture"}`. For arbitrary fictional inquiries set `mode` to `live` after configuring credentials. Alternatively supply `assessment` with the original Prime24AI `name`, `email`, `company`, `workflow`, `service` text fields instead of `inquiry`. The adapter preserves them without opening Gmail. The offer selected in `service` remains separate from the home-service request described in `workflow`. The exact assembled assessment is not a curated fixture and needs live mode for extraction.

The API and Streamlit share `lead_eval.workflow` and the same database; Streamlit calls this application layer directly, so an HTTP process is optional for the dashboard. Backend submissions appear in the corresponding dashboard approval queue. The API returns 201 for a pending draft, 200 for other persisted workflow outcomes, 400 for bad request envelopes, 409 for invalid approval transitions, and 503 for unconfigured live mode. Inspect the returned `status` for business errors.

The HTTP server binds only to loopback and rejects browser Origin headers and unrecognized Host headers. There is no authentication, user management, production frontend wiring or public deployment. Do not expose it through a tunnel or reverse proxy. Staff names are local attribution, not verified identities. No changes have been pushed to GitHub or deployed to the production website.

## Live model configuration

No credential was available during this build. Live evaluation was skipped; all committed evaluation output is clearly labeled fixture or simulated. API adapter tests use a fake key and an in-memory HTTP transport, never the network.

Copy `.env.example` for reference. Export variables into your process using your shell or secret manager. The app does **not** automatically load `.env` files. `OPENAI_API_KEY` is required only for live mode; never paste keys into the UI or commit them. `.env*`, virtual environments and working databases are ignored by Git. One provider endpoint is used: OpenAI Chat Completions at `https://api.openai.com/v1/chat/completions` with strict JSON Schema and a default model of `gpt-4.1-mini`.

After supplying credentials in the environment:

```bash
python -m lead_eval --mode live --output reports/live-evaluation.json
```

A live evaluation processes 20 unique live inquiries, 5 duplicate cases without model calls, and 5 separately labeled injected scenarios without model calls. Transient failures can increase the live call count up to 60. Each duplicate's setup seed is a fixture, outside the measurement population. Model/network/schema errors remain actual failed cases; results are never replaced with fixtures.

Configuration: `OPENAI_MODEL`, `API_TIMEOUT_SECONDS` (default 20; allowed 0–120 exclusive of zero), `DATABASE_PATH` (default `data/dashboard.sqlite`), `INPUT_USD_PER_MILLION` (0.40) and `OUTPUT_USD_PER_MILLION` (1.60). Pricing is an **explicit assumed standard uncached rate**, not a claim about current pricing or billed charges. Verify https://openai.com/api/pricing/ for your selected model before running. Override both rates when changing models. Estimate = `(reported input tokens × input rate + reported output tokens × output rate) / 1,000,000`; no cached/batch discounts are modeled.

Completed responses contribute their reported usage even when output validation fails. Timeout/HTTP failures may have unknown billable usage; the UI reports usage coverage and known partial estimates instead of treating unknown usage as zero. Fixture and simulated tokens/cost are N/A. The app stores the requested/returned model and settings, allowing attribution of actual measurements.

## Architecture

```text
Streamlit app.py ──────────┐
HTTP lead_eval/server.py ──┼─> workflow.py ─> client.py ─> OpenAI OR offline fixture
Evaluation CLI ───────────┘       │              └────> injected failure client
      evaluation.py              ├─> schema.py + guards.py
            │                    └─> db.py ─> SQLite
            └─> deterministic scoring ─> SQLite run history + JSON reports
```

`prime24.py` adapts existing assessment fields. `config.py` reads environment configuration. `schema.py` uses Pydantic to enforce types, enumerations, nullable fields, no extra keys, email/phone shape and internally consistent missing fields. Contact/location strings must also occur in the inquiry. `guards.py` enforces required clarification phrases and rejects certain unsupported draft claims. Human semantic review remains mandatory.

Input validation and duplicate reservation happen before any model call. Duplicate keys normalize Unicode/case/whitespace/punctuation and are scoped separately for manual fixture/live work and each evaluation case. A SQLite transaction plus partial unique index prevents concurrent matching submissions from both calling the API. Pending/approved/processing records reserve their keys; failed/invalid attempts permit resubmission.

Timeouts, connection errors, HTTP 408/429 and 5xx responses retry at most twice (three attempts total), with 0.1s and 0.2s backoff. Every attempt has configured HTTP connect/read/write/pool timeouts. Validation failures and permanent API errors fail immediately. These HTTP operation timeouts are not a hard deadline for the complete workflow. No queue, worker framework or circuit breaker is required for this prototype.

SQLite tables: `inquiries` stores state, extraction, draft, mode, usage and attempt log; `approval_events` stores successful approval transitions; `evaluation_runs` stores timestamps, configuration, prompt/schema/code/dataset hashes and summary; `evaluation_results` stores each expected/actual comparison. Foreign keys are enabled on every connection, and completed runs survive process restarts. Raw malformed outputs and provider error bodies are not saved. SQLite contains fictional data and should still be handled as local application data.

## Dataset and scoring

The [acceptance contract](docs/acceptance-criteria.md) and independent labels were saved before implementing the workflow. [data/cases.json](data/cases.json) contains 10 complete, 5 missing-information, 5 duplicate, 5 ambiguous and 5 simulated-failure cases. [data/fixtures.json](data/fixtures.json) holds separately authored canned responses; runtime fixtures do not read expected labels. Both are versioned, inspectable data. All names/addresses are fictional, emails use example.com, and phone numbers use the reserved 555-01xx range.

Eight extraction fields are scored: name, email, phone, service, address/location, urgency, missing-information set, ambiguity. Exact equality follows documented Unicode/whitespace/case normalization; phone formatting is ignored. Null must match null, and absent output receives no credit. Each case also requires correct workflow status, independently labeled error/retry expectations where applicable, and deterministic draft guardrails. Required draft phrases come from test labels. No model grades its own output.

A pass means expected behavior occurred: an exhausted timeout safely ending in error can pass. Accuracy = correct extraction fields / applicable extraction fields. Error/duplicate cases without expected extraction have no extraction denominator; their state and error behavior still count toward pass rate. Each field/source reports its numerator and sample count. Null-heavy fields can inflate microaccuracy; examine complete-case pass rates and individual outputs as well.

Latencies use monotonic elapsed time for input validation, model attempts/backoff, output checks and initial persistence. A final telemetry update is outside that interval. Median and nearest-rank p95 are recomputed from case rows, never averaged across groups. Attempted-call workflow latency excludes duplicate/no-call paths and includes workflow overhead; it is not pure provider network latency. Full workflow timings and sample counts are also displayed. Fixture, live and simulated populations are separate. Run history retains all runs, including incomplete-run indicators.

## Verified results and deliverables

See [measured results](reports/results.md), [full fixture report](reports/fixture-evaluation.json), [pytest output](reports/pytest.txt), [JUnit](reports/pytest.xml), and [live status](reports/live-status.json). The normal fixture population has 25 cases, including 20 extraction cases (160 field checks) and 5 duplicate cases. The 5 injected scenarios have a separate denominator, including one recovered extraction case. Tests deliberately corrupt each scored field to verify that wrong outputs fail.

The final run passed **30/30 expected-behavior cases** and **160/160 regular-fixture extraction checks**; **61 pytest tests passed**. These results verify software behavior against canned data and injections. They do not measure live model quality, production throughput, customer satisfaction or reliability. The rendered dashboard was also checked in the browser; Streamlit's AppTest exercised evaluation, intake and explicit approval.

[Failure analysis](docs/failure-analysis.md) documents a malformed-output scenario and its actual observed behavior. [Two-minute demo](docs/demo-script.md) and [résumé bullet](docs/resume-bullet.md) are ready to use. Raw saved evaluation JSON includes run IDs, timings, settings, source labels and sample counts for independent inspection. Mutable databases are ignored; recreate them with the CLI. Two fixture runs are retained in the delivered workspace database.

## Limitations and next steps

This is a small English-language home-services benchmark with curated drafts. It does not establish generalization, live model accuracy or production reliability. Deterministic substring checks can miss plausible hallucinations and can reject harmless wording. The model can still infer service/urgency incorrectly; staff must inspect every draft. No message transmission route exists, even after approval.

There is no auth/RBAC, encryption at rest, retention automation, public deployment, emergency dispatch, semantic duplicate matching or automated recovery of a process killed mid-request. A hard crash may leave a `processing` reservation; inspect the corresponding local record before manually clearing it. HTTP request threads and SQLite are suitable for a local demo, not a load-tested public service. The production website has not been connected to this backend. Next useful validation is a live run with explicit pricing, followed by independently reviewed holdout inquiries and adversarial input cases.

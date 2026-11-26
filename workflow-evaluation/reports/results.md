# Measured verification results

Run ID: `a4b2047e9ff342749b4202da20c740e7`. Dataset v1. **FIXTURE + separately labeled SIMULATED injections**. No live model requests.

61 pytest tests passed; see pytest.txt and pytest.xml. HTTP tests use a real local server with fixture inputs. OpenAI transport tests use mocks and fake credentials. Browser inspection confirmed the rendered dashboard; AppTest exercised evaluation, processing and staff approval.

| Population | Cases passed / n | Extraction matches / checks | Attempted-call workflow median | p95 | Timing n |
|---|---:|---:|---:|---:|---:|
| Fixture | 25/25 | 160/160 | 3.79 ms | 5.52 ms | 20 |
| Simulated | 5/5 | 8/8 | 4.09 ms | 304.65 ms | 5 |
| Live | Not run (n=0) | Not measured | Not measured | Not measured | 0 |

Attempted-call workflow times include validation, persistence and retry delays. They are local fixture/injection timings, not API response times. Fixture full-workflow timing includes the 5 no-call duplicates: median 3.77 ms, p95 5.52 ms, n=25.

| Category | Passed / n |
|---|---:|
| complete | 10/10 |
| missing | 5/5 |
| duplicate | 5/5 |
| ambiguous | 5/5 |
| failure | 5/5 |

All 30 cases passed expected behavior; terminal statuses are {"pending_approval": 21, "duplicate": 5, "error": 4}. A controlled error is an acceptance pass only when its cause and retry count match the independently defined expectation.

Token usage and estimated API cost: **N/A** for fixtures and injections. Number of live calls: **0**. No invented token counts or cost estimates. Assumed pricing for future live calls: $0.40 input / $1.60 output per million tokens, subject to verification and environment overrides.

All eight regular-fixture fields matched 20/20 applicable expected values (160/160 combined). The recovered simulated timeout matched 8/8 separately. Null matches are included; this small curated corpus is not a generalization study.

Live evaluation: skipped because OPENAI_API_KEY was unavailable. CLI rejection was verified before any run or model request. Known remaining blocker: credentials for live measurement only.

This 30-case fictional dataset and canned-response agreement are not evidence of production reliability. Timings vary by host and SQLite filesystem.

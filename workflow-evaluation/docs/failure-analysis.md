# Failure analysis: malformed model output (F03)

Source: saved fixture run `a4b2047e9ff342749b4202da20c740e7`, case F03. This is an intentional injection, not an observed live provider incident.

The simulated client returned `{broken JSON` for an otherwise valid complete inquiry. The independently defined expectation was terminal error `malformed_output`, one attempt, zero retries, and no approvable draft.

Observed: status `error`, error `malformed_output`, 1 attempt, 0 retries, 3.99 ms local workflow time. Pydantic rejected the JSON. The persisted extraction is null; the sanitized error records a `json_invalid` type without retaining the raw response. The expected error behavior passed evaluation. Automated tests separately verify that errored records cannot be approved and a failed inquiry can be resubmitted.

Validation errors are permanent for the attempt, so the workflow does not blindly pay for repeated malformed output. Staff sees an error and must resubmit deliberately after inspection. No response is sent, and the failed attempt does not reserve the duplicate key permanently. This policy trades automatic recovery for predictable cost and a clear failure boundary.

For comparison, F01 intentionally timed out once and recovered: 2 attempts, 1 retry, pending_approval. F02 exhausted its bound: 3 attempts, 2 retries, api_timeout. These injection timings and unknown usage are excluded from live model metrics.

A future live study should measure malformed-output frequency, add independently reviewed holdout inquiries and evaluate a single explicit repair strategy against cost and quality criteria. This controlled scenario does not estimate real provider failure rates.

## Observed live validation failures

The paced live run passed 6/20 extraction cases (48/160 fields), 5/5 duplicate checks and 5/5 injected scenarios. Each live inquiry made one attempt. Fourteen responses failed validation, including all five ambiguous cases. The historical report retained only a generic validation error. Future runs record specific rule codes. No improvement in live accuracy has been measured since this change.

# Acceptance contract — dataset v1

Written before workflow implementation. This is a small fictional home-services intake benchmark, not evidence of production reliability. Expected labels are authored as ground truth, separately from fixture responses. Never generate ground truth from model output.

## Fields and normalization

The model must return one JSON object with exactly these fields: `contact_name`, `email`, `phone`, `service`, `location`, `urgency`, `missing_information`, `ambiguous`, and `draft_response`. Strings can be null only for name, email, phone, and location. No additional keys. Service: plumbing/electrical/hvac/cleaning/unclear. Urgency: urgent/soon/routine/unknown. Missing information is a unique list drawn from contact_name/contact_method/service/location/urgency. Ambiguous is a strict boolean. Draft is 20–2000 characters.

Required intake information: name, at least one email or phone, a supported and unambiguous service, service location, and urgency. Unknown or uncertain values remain null/unclear/unknown; do not infer facts. Urgent means explicit immediate/emergency/today or active leak/sparks; soon means this week/within days; routine means explicit routine/flexible/no rush. Otherwise urgency is unknown. Conflicting contacts, multiple possible services, and unclear intent require ambiguity=true and clarification; unsupported requests map to unclear.

Extraction acceptance is deterministic equality to independently labeled fields after Unicode NFKC, case folding and whitespace collapse; emails are case insensitive; phone numbers compare digits; missing-information lists compare as sets. Null must match null. Location and contact names must match the supplied values after normalization (no fuzzy credit). Nine scored fields: all model fields except draft_response, plus expected workflow status. Field accuracy = matching applicable fields / applicable fields. Failed/invalid/duplicate cases with no extraction score workflow status only; report extraction-only accuracy separately (8 extraction fields, n and denominator shown).

Draft acceptance uses deterministic required substrings supplied per case (known service/contact details and requested clarification) and prohibits URLs, invented dollar amounts, claims of sending, booking, approval, and promises of attendance. Every non-error draft must say that staff will review it. These checks are guardrails, not a complete measure of tone, truthfulness or usefulness; staff must read every draft. An evaluation pass requires every applicable extraction field, exact workflow status, and all draft checks to pass. No model grades its own response.

## Workflow invariants

- A valid unique inquiry is persisted as pending_approval, regardless of missing details or ambiguity. No automatic approval.
- A staff identifier and explicit approval transition are required to approve a pending draft. Approval is local; nothing is sent. Invalid, duplicate and failed records cannot be approved. Repeated approval is rejected. Local staff attribution is not authentication.
- Inquiry must be text, 10–4000 trimmed characters, without control characters other than tab/newline/carriage return. Invalid input makes zero API calls.
- Duplicate = SHA-256 of NFKC/casefold/whitespace-normalized text with punctuation treated as word separators, within an explicit scope. Already pending or approved inquiries block matching submissions. Error/invalid attempts do not block retry. This catches formatting variants, not semantic paraphrases.
- Schema errors and nontransient API errors fail immediately. Timeout, connection and HTTP 408/429/5xx failures retry at most twice (three total attempts), with bounded exponential delays. Each attempt has a finite timeout. Tokens reported by completed calls are accumulated, including malformed responses; unreported usage stays unknown.
- Inquiries, validated outputs and sanitized error details are stored locally. Raw malformed output and provider error bodies are not retained; secrets are never stored. No send integration exists.

## Benchmark populations

Exactly 30 cases: 10 complete, 5 missing required information, 5 duplicate variations, 5 ambiguous, 5 injected failures. Each case gets an isolated duplicate scope. Duplicate cases include an explicit seed processed before the measured attempt. Five failure scenarios: timeout recovered, timeout exhausted, malformed JSON, schema mismatch, and permanent API error. Failure injections are always labeled simulated, even during a live run, use no live API, and are excluded from live latency/token/cost metrics. All other fixture calls are labeled fixture. Samples and denominators accompany every aggregate.

Case elapsed time uses monotonic wall time around the workflow, including retries, validation and persistence. p95 uses the nearest-rank method ceil(0.95*n). Fixture timings measure local software only. Token usage is provider-reported on live calls, unavailable on injected calls, and not applicable for fixture/duplicate/invalid paths. Estimated cost uses configured input/output USD per million token rates; no claim of billed cost. Unknown usage is never silently treated as known zero.

## Expected failure behavior

F01: timeout then success, 2 attempts/1 retry and pending_approval. F02: timeout exhausted, 3 attempts/2 retries and api_timeout. F03 and F04: malformed JSON/schema, 1 attempt/0 retries and malformed_output. F05: permanent HTTP 401, 1 attempt/0 retries and api_http_401. Failure-cause and retry-count mismatches fail acceptance even if the terminal status is error.

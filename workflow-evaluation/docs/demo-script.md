# Two-minute demo script

Preparation: run `python -m lead_eval --mode fixture`, then `python -m streamlit run app.py`. Start with an unused manual sample or a fresh local database. Keep live mode disabled unless credentials are configured. All figures below refer to the saved fixture report.

**0:00–0:20 — Explain the project**

“This is a supervised AI lead-processing prototype in my Prime24AI repository. It extracts a fictional customer's contact details, service, urgency and missing information, then drafts a response. A staff member must approve it locally. There is no send integration.”

**0:20–0:45 — Process a missing-information inquiry**

Open **Process inquiry**. Select fixture sample **M01**, then **Process inquiry**.

“This inquiry lacks a contact method. The typed output flags that field and the draft asks for an email or phone number. Fixture mode uses curated responses and makes no model calls. Arbitrary fictional inquiries can use the OpenAI adapter in live mode.”

**0:45–1:05 — Show approval and duplicate handling**

Open **Staff approval**, choose the pending fixture record, enter “Demo reviewer,” tick the review checkbox and approve. Return to intake and submit M01 again.

“Approval requires an explicit review action and creates a SQLite audit event. The repeated inquiry is detected before calling a model.”

**1:05–1:35 — Explain evaluation evidence**

Open **Evaluation dashboard**. Show category counts, fixture extraction accuracy, and timing sample sizes.

“I defined field-level criteria and 30 independent expected results before implementation. The fixture benchmark passed 30 of 30 behavior checks, with 160 of 160 extraction checks in the regular fixture population. This verifies the harness; it does not prove live model quality or production reliability. The separate live run produced six accepted drafts from twenty inquiries. Fourteen responses failed validation.”

**1:35–2:00 — Show a failure and backend**

Inspect case **F03** and its attempt log. Briefly show the backend routes in the README.

“Malformed JSON is rejected after one attempt, with no approvable draft. Timeout scenarios use bounded retries and are measured separately. The project also has local HTTP submission, lookup and approval endpoints. All 62 tests passed, covering scoring, duplicates, approvals, retry behavior, malformed output, persistence, backend routes and the UI.”

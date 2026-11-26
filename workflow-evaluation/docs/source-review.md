# Prime24AI source review

Source: https://github.com/darnleyweekes-spec/prime24ai
Inspected main commit: f366c8dca679a237bd7fb605aec5a59a04b46ccc.

The repository is a Vite/static website, not a Python AI lead-execution service. `alpha.js` lines 257–267 serializes an assessment's name, email, company, workflow and service into Gmail compose. `how-it-works/index.html` links to a fictional lead demo hosted at agents.prime24ai.com/lead-follow-up, but that demo's execution source is not in this repository. `follow-up/core.js` builds document reminders with deterministic checklist logic; it is a bookkeeping tool, not lead extraction.

This addition lives in `workflow-evaluation/` in the existing repository. It reuses the source workflow's intake → prepare draft → staff review boundary and adds a small Python adapter for the existing assessment fields. The separately scoped fictional home-service benchmark exercises the Service Request Workflow Pilot concept. AI extraction, evaluation, SQLite storage and staff approval are new implementation, not a claim that the website's form already had these features. Original website files and production behavior are unchanged. No Gmail/Stripe/analytics or external write integrations are imported.

The acceptance contract and independent 30-case labels were saved before Python workflow implementation. The repository link arrived after those labels were authored; source inspection confirmed the standalone Python execution layer was needed.

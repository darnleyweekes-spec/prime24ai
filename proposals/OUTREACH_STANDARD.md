# Prime24AI proposal-room outreach standard

Use a dedicated proposal room in every new cold-email campaign for these five products. The room replaces generic embedded graphics, attachments, and links to the proposal chooser.

## Approved room URLs

| Product | Base room |
| --- | --- |
| Prime24AI | `https://prime24ai.com/proposals/prime24ai/` |
| Agents | `https://prime24ai.com/proposals/agents/` |
| Learn | `https://prime24ai.com/proposals/learn/` |
| PitchMe | `https://prime24ai.com/proposals/pitchme/` |
| Paws & Power | `https://prime24ai.com/proposals/paws-and-power/` |

## Required personalization

Add both URL parameters:

```text
?company=COMPANY_NAME&workflow=SPECIFIC_WORKFLOW
```

Encode the values before inserting them. Use the prospect's public company name and a concise workflow hypothesis. Never include a person's email address, confidential information, medical information, credentials, or customer records in the URL.

Example:

```text
https://prime24ai.com/proposals/agents/?company=Acme%20Accounting&workflow=missing-document%20follow-up
```

## Email structure

Keep the message under 130 words.

1. One verified observation about the company or workflow.
2. One sentence naming the narrow pilot and desired operational outcome.
3. The full clickable personalized proposal-room URL.
4. One low-friction question that can be answered by email.
5. Prime24AI identity and reply-to. No phone-call request.

Do not use generic compliments, “hope you’re well,” hype, unverifiable ROI claims, embedded proposal graphics, attachments, or disguised anchor text. The proposal room contains the visual, comparison, assumptions, and selectable scope.

## Qualification and safety gates

- Verify the contact and confirm they have not been contacted previously.
- Verify the company observation from a current public source.
- Treat the workflow and ROI as hypotheses until the prospect confirms them.
- Re-check competitor sources before material campaigns.
- Keep sends low-volume through Gmail while current deliverability constraints remain.
- Draft first. Sending still requires explicit approval.

## Campaign measurement

Track by product and segment, not only aggregate results: sent, delivered, bounced, replied, qualified reply, proposal opened when tracking is available, and paid conversion. Compare segments to detect reversals hidden by aggregate performance.

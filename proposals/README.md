# Prime24AI interactive proposal rooms

This directory powers a no-index, client-side proposal experience for five Prime24AI products. It is intentionally separate from the public marketing homepage.

## Personalized links

Use the product-specific room and URL parameters for all external outreach:

```text
https://prime24ai.com/proposals/agents/?company=Acme&workflow=inbound%20lead%20qualification
```

Permanent rooms:

- `/proposals/prime24ai/`
- `/proposals/agents/`
- `/proposals/learn/`
- `/proposals/pitchme/`
- `/proposals/paws-and-power/`

The `/proposals/` page remains the internal product chooser. Do not use it in external email campaigns.

The page removes angle brackets, trims inputs, and limits their length before rendering them with `textContent`. No prospect information is sent to a backend or stored by this page.

## Outreach model

The email should contain one concrete observation, one sentence describing the proposed pilot, and the personalized proposal-room link. The room handles the comparison, ROI assumptions, scope selection, and reply path. Do not attach generic graphics.

Competitor rows are buying-fit comparisons based on linked public pages. Re-check the sources before a material campaign because pricing and positioning can change.

See `OUTREACH_STANDARD.md` for the required email structure, personalization rules, safety gates, and segmented campaign measurement.

# Prime24AI interactive proposal rooms

This directory powers a no-index, client-side proposal experience for five Prime24AI products. It is intentionally separate from the public marketing homepage.

## Personalized links

Use URL parameters to prepare a room without creating a new page:

```text
https://prime24ai.com/proposals/?product=agents&company=Acme&workflow=inbound%20lead%20qualification
```

Supported products:

- `prime`
- `agents`
- `learn`
- `pitchme`
- `paws`

The page removes angle brackets, trims inputs, and limits their length before rendering them with `textContent`. No prospect information is sent to a backend or stored by this page.

## Outreach model

The email should contain one concrete observation, one sentence describing the proposed pilot, and the personalized proposal-room link. The room handles the comparison, ROI assumptions, scope selection, and reply path. Do not attach generic graphics.

Competitor rows are buying-fit comparisons based on linked public pages. Re-check the sources before a material campaign because pricing and positioning can change.

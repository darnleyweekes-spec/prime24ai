# Client Follow-Up Kit — owner operating guide
Owner: Darnley Weekes / Prime24AI. Prepared 2026-09-09.

## What you sell
A $149 one-time personalized setup for ONE monthly bookkeeping document workflow. The browser tool and starter reminders are free. The paid value is adapting the checklist and language, configuring the reusable workflow, and handing it over.

Included: up to 20 request types, five reminder templates, CSV tracker, reusable browser tool, one 30-minute handoff, one revision requested within seven days of delivery.
Delivery: within two business days after payment and complete intake.
Excluded: client document handling, bookkeeping/tax work, accounting integrations, automatic email sending, cloud synchronization, ongoing support subscriptions.
No revenue or time-saving results are guaranteed.

## Order and fulfillment
1. Check Stripe for a successful payment; match the buyer email and $149 product. Never treat a screenshot, website visit or email as proof of payment.
2. Ask for firm name, work contact, a blank recurring checklist, their existing secure portal address, preferred wording and agreed document dates. Do not ask for actual client documents or portal credentials.
3. Confirm the scope and delivery date in writing. If the existing software already solves the problem, be candid before selling.
4. Copy the starter reminders; replace every placeholder with approved firm wording. Create the firm's checklist as CSV and JSON using client aliases. Leave dates blank if the firm has not supplied them.
5. Tailor the browser kit's copy and default sample labels if needed. Do not embed real client data or private portal access tokens in public site code.
6. Validate: imports work, statuses are preserved, received items are excluded, corrections are explicit, no bracketed placeholders remain in the deliverable, portal is correct, and empty lists generate no false request.
7. Deliver the tailored templates, CSV and JSON backup using the agreed business channel; point to the reusable public tool. The buyer can import the backup.
8. Run the 30-minute handoff: 5 minutes scope, 10 minutes adding/updating requests, 10 minutes preparing/exporting drafts and backups, 5 minutes questions.
9. Handle one revision requested within seven days. Record delivered date, revision due date and time spent.
10. Ask for permission before using feedback, client names, logos or results in marketing.

## Delivery email
Subject: Your Client Follow-Up Kit is ready

Hi [name],

Here is your tailored checklist, the five reminders and your tracker.

To use the browser tool, open https://prime24ai.com/follow-up/ and choose Restore backup. Load the JSON file I sent. Mark received items, choose a client and prepare a draft.

Review the item names, dates and portal address before sending. Download a fresh backup before closing the tab.

For the 30-minute handoff, do either [time 1] or [time 2] work?
Your included revision can be requested by [date seven days after delivery].

Darnley

## Cancellation and corrections
A full refund is offered if the customer cancels before work begins. If the deliverable misses the agreed scope, correct it on request within seven days; refund the setup fee if that scope cannot be delivered. Do not promise chargeback or legal outcomes. Track refunds separately from sales.

## Costs and first-sale arithmetic
New spending authorized ceiling: $20.
Spent in this build: $0.
New domains: $0 (use existing prime24ai.com).
New subscriptions: $0.
Advertising: $0.
Cash reserve: $20.
Existing account costs and your time are not included in the $0 incremental figure.

At Stripe's published standard US domestic-card rate of 2.9% + $0.30, a $149 payment incurs approximately $4.62 processing fees, leaving $144.38 before labor, taxes, refunds and other costs.
This is not profit. If fulfillment takes two hours and you value your time at $40/hour, the illustrative remainder is $64.38 before other costs.
If all $20 is later spent, the equivalent remainder becomes $44.38. Do not buy ads until the offer gets paid interest.
Source: https://stripe.com/pricing/
Account-specific processing rates and other payment methods may differ. Automatic tax was not enabled by this task; existing tax obligations and account settings still need the owner's normal review.

## Payment configuration
Stripe account: Prime24 AI.
Live one-time price: price_1UDsSM8rESriZdYGKrgTD87u
Product: prod_VEL8zucDTUtOmc
Payment link: https://buy.stripe.com/8x2eV7aU720wfUU1zr4800b
Payment link ID: plink_1UDsSh8rESriZdYGFKBTWnFy
No subscription, custom payment domain or invoice-creation add-on.
Hosted confirmation asks the buyer to email intake. There is no webhook or automatic delivery. The owner must review orders and fulfill them manually.

## Sales tracker fields
Company, public contact route, contact-history checked, date contacted, reply, demo date, order status, gross amount, fees, refund amount, delivery date, delivery hours, next action.
Do not store actual sales records in this public repository.

## Technical scope
Static page in follow-up/index.html, isolated follow-up/kit.css, core.js and kit.js. No dependency installation or backend required.
Existing root homepage adds a link and a dedicated offer section. Existing site layout, other offers and ALPHA behavior are preserved.
All user-entered table text uses textContent. Drafts use textarea values, not innerHTML. JSON backup imports are bounded by file size, row count, enums and string limits. CSV export neutralizes formula-leading values. Only HTTPS portal URLs without embedded credentials are accepted.
State lives only in the current tab. Download a JSON backup to retain it. CSV is an output format; restore takes JSON.
No browser-level or real payment transaction test was performed in this session. JavaScript syntax and core behavior were checked. Verify the visible page, downloads, email draft handoff and hosted checkout before promoting broadly.

## Launch validation
- Page loads at https://prime24ai.com/follow-up/.
- The live homepage links to it.
- The Stripe link shows the correct offer and $149 amount.
- Sample workflow produces only open requests.
- Marking all items received produces a receipt confirmation.
- Request form explicitly prepares an email; it never claims the email was sent.
- Files and links referenced by the static page exist.
- Prospect emails are drafts only. Three are published addresses, not inbox-deliverability verified.

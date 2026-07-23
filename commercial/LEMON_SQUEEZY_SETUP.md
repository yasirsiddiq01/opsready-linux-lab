# Lemon Squeezy setup plan for OpsReady Linux Lab

This document prepares the product for Lemon Squeezy without activating payments prematurely.

## Recommended product position

- Product name: **OpsReady Linux Lab Pro**
- Product type: hosted, self-paced Linux training application
- Delivery: immediate access to a private web application after payment
- Proposed tax category: **On Demand Online Courses** because the product provides interactive online training. Confirm the category during onboarding.
- Currency: EUR
- Pricing display: tax-inclusive where appropriate for consumer sales
- Recommended variants: Monthly and Annual
- Free trial: not required at launch because the Community edition already acts as the free evaluation tier

## Safety gate before live checkout

Do not enable checkout until all of the following are true:

1. A private Pro deployment exists.
2. A purchase creates or activates access reliably.
3. Cancellation or expiry removes paid access at the correct time.
4. The support email is monitored.
5. Terms, privacy, and refund policies are published at stable HTTPS URLs.
6. Test-mode purchases, cancellations, refunds, and failed payments have been exercised.
7. Seller identity, tax, and self-employment obligations in Spain have been reviewed with a qualified adviser.

The Community application's `Plans` page enforces this using two configuration gates:

```toml
[commercial]
sales_enabled = false
fulfilment_ready = false
```

Both gates must be true, and all checkout and policy links must be valid HTTPS URLs, before the live upgrade button appears.

## Store creation sequence

### Phase 1 — Test mode

1. Create the Lemon Squeezy account using the seller's real Spanish residence and legal identity.
2. Create a store called `OpsReady Linux Lab`.
3. Keep the store in Test mode.
4. Add one product: `OpsReady Linux Lab Pro`.
5. Add two subscription variants:
   - Pro Monthly
   - Pro Annual
6. Enter product copy from `commercial/PRODUCT_LISTING_COPY.md`.
7. Add product screenshots and a simple product thumbnail.
8. Select the most accurate tax category.
9. Configure the success redirect to the private Pro onboarding page, not the public Community app.
10. Create and test the customer portal.

### Phase 2 — Access integration

Use one of these fulfilment models:

- **Account + webhook model (recommended):** checkout passes the learner's internal user ID; Lemon Squeezy webhooks update subscription status in the application database.
- **License-key model (simpler early release):** Lemon Squeezy issues a key and the private Pro application validates it. This is easier initially but weaker than a full account system for progress and institutional plans.

For subscriptions, the minimum webhook events should cover creation, update, cancellation/expiry, and payment recovery states. Webhook signatures must be verified before processing any event.

### Phase 3 — Verification and activation

Prepare:

- government-issued ID
- real Spanish residential address
- tax details requested during onboarding
- store and product description
- public Community product URL
- private Pro fulfilment explanation
- support email
- refund policy URL
- privacy policy URL
- terms URL
- payout details for the Lloyds account in the account holder's legal name

Submit store activation only after the private access flow can be demonstrated. Store review normally includes a business questionnaire and identity verification.

### Phase 4 — Live-mode release

1. Copy the tested product and discounts to Live mode.
2. Replace test URLs with live checkout URLs.
3. Configure production webhook signing secrets.
4. Run one low-value real purchase using a separate customer email.
5. Verify access, receipt, subscription status, customer portal, cancellation, and support response.
6. Set `sales_enabled = true` only after the end-to-end check passes.

## Recommended launch policy

Start with a limited founding-user release rather than a broad public launch. Ten paying users are enough to validate:

- whether the learning outcome is clear;
- whether learners complete multiple sessions;
- whether the Pro features justify recurring payment;
- how much support each user requires;
- which command, incident, and assessment areas need correction.

Do not offer a lifetime deal while hosting and support costs remain uncertain.

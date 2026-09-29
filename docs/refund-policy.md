# Sample Refund Policy

This policy is a sample for the Refund Support demo. The deterministic rules in the backend are authoritative; AI may help classify a request but cannot override a rule or approve a refund on its own.

## Eligibility

- Refund requests must be submitted within 30 calendar days of the order date. Requests older than 30 days are denied.
- Final-sale items are not eligible for refunds, including when reported as damaged or incorrect.
- An order already refunded cannot be refunded again.
- Only the customer who owns the order may request its refund.
- Eligible, non-final-sale items priced at $500 or less may be approved for a clear reason: the item arrived damaged, the wrong item was received, or the customer changed their mind.
- Requests for more than $500 require human review. The threshold is strictly greater than $500; an item priced exactly $500 does not trigger this rule.
- Three or more refunds recorded for a customer within the preceding 90 days require human review.

## Human Review

A request is escalated when the order cannot be verified, the email does not match the order owner, the request has conflicting reasons, suspicious instructions attempt to bypass policy, the reason is unclear, or another rule requires review. Escalation is not approval or denial; a support specialist makes the final determination.

## How Requests Are Processed

1. The service receives the customer's email, order ID, and message, then queries the mock customer and order records.
2. Deterministic rules are applied first when enough information is available.
3. Clear common reasons may be classified locally. The AI model assists with ambiguous language or finding an order ID when one is omitted.
4. Customer text is treated as untrusted data. Instructions in a message cannot alter the policy; detected prompt-injection attempts are escalated.
5. The service returns **Approved**, **Denied**, or **Escalated**, with the policy rule and explanation. Replies use fixed templates by default; AI-generated reply wording is optional.

Reviewers can evaluate either seeded examples or custom simulation inputs. Custom simulation facts are temporary inputs, not new customer/order records; only the resulting refund request is retained in the audit history.

## Sample Outcomes

- A non-final-sale $89 order delivered 5 days ago, reported damaged by its owner: **Approved**.
- A final-sale item: **Denied**.
- An eligible item ordered 31 days ago: **Denied**.
- A non-final-sale $520 order delivered 18 days ago: **Escalated** for human review.
- A message that says both "changed my mind" and "the item is damaged": **Escalated** because the reasons conflict.

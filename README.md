# Refund Support

A demo refund-support app with a React customer chat, a Django REST API, seeded mock customers and orders, deterministic policy evaluation, and optional Gemini assistance.

## Run Locally

Requirements: Docker Engine with the Docker Compose plugin, or Docker Desktop with Compose.

```sh
docker compose up --build
```

The frontend is at <http://localhost:3000>. The API is at <http://localhost:8000/api/>. On startup, the backend applies migrations and seeds 15 mock customers and 23 orders. No separate mock-data service or API key is required to start the app. The legacy command `docker-compose up --build` works with installations that provide the standalone Compose command.

To stop the services:

```sh
docker compose down
```

The seed command recreates the mock customer and order records at backend startup. This is demo data, not persistent production data; restarting the backend resets those records. Refund requests are stored in the backend's SQLite database inside its container.

## Environment Variables

AI is optional. Without a key, deterministic checks and clear locally-classified requests still work. Requests requiring AI classification may be escalated when classification is unavailable.

To configure Gemini, copy the example file and edit it locally:

```sh
cp .env.example .env
```

Set `API_KEY` to a Gemini API key in `.env`, then start or rebuild the backend with `docker compose up --build`. Do not commit `.env` or share the key. `.env` is ignored by Git.

| Variable | Default | Purpose |
| --- | --- | --- |
| `API_KEY` | empty | Gemini API key. Needed for AI classification when the order ID is omitted or the reason is ambiguous. |
| `AI_MODEL` | `gemini-3.8-flash` | Gemini model name used by the backend. |
| `AI_REPLY_ENABLED` | `false` | Set to `true` to request AI-written replies after an AI classification. This can use an additional model request; fixed replies are used by default. |

## Architecture

- `frontend/`: React and Vite app. The chat loads customer/order choices and submits requests; the support dashboard lists recent decisions.
- `backend/`: Django REST Framework API, SQLite models, and a management command that seeds demo data when the container starts.
- `backend/refunds/services/policy.py`: deterministic source of truth for refund outcomes. The model does not override these rules.
- `backend/refunds/services/workflow.py`: request orchestration: sanitization, order lookup, policy pre-checks, optional classification, safeguards, final result, and persisted audit record.
- `backend/refunds/services/ai.py`: optional Gemini classification and reply generation, local reason matching, prompt-injection checks, and fallback replies.
- `docs/refund-policy.md`: sample business policy matching the implemented decision rules.

Request flow: the chat sends customer email, order ID, and message to `POST /api/refund-request/`. The backend looks up the mock order, applies deterministic pre-checks, and uses local matching for clear reasons. Gemini can classify ambiguous reasons or find an order ID when omitted. The backend then returns and stores `Approved`, `Denied`, or `Escalated`. The support dashboard loads the saved results from `GET /api/requests/`; customers and their orders are provided by `GET /api/customers/`.

The policy engine decides the outcome. AI is an assistive classifier/reply writer only, and customer text is treated as untrusted input. Detected injection attempts and conflicting reasons are escalated. AI failures fall back safely rather than changing a policy outcome.

## Policy Summary

The configured return window is 30 days. Final-sale and already-refunded orders are denied; orders belonging to another customer or not found are escalated. Non-final-sale amounts above $500, three or more refunds in the preceding 90 days, unclear reasons, conflicting reasons, and suspected prompt injection require human review. Clear damage, wrong-item, or changed-mind requests for eligible orders may be approved. See [the full sample policy](docs/refund-policy.md).

## Tests

Run the backend tests in the running container:

```sh
docker compose exec backend python manage.py test refunds
```

The tests cover policy boundaries, order ownership, seeded data, local classification, AI-free paths, and prompt-injection/conflicting-request escalation.

## Demo Walkthrough

A short recording should show:

1. Open the running app at `http://localhost:3000` and select a customer and order.
2. Submit a clear damaged-item request and show an eligible decision.
3. Show a final-sale, older-than-30-days, or over-$500 request and explain the result.
4. Submit a conflicting or prompt-injection message and show escalation.
5. Open the Support dashboard and show the saved requests and audit reasons.
6. Briefly explain the React-to-Django request flow, deterministic policy-first evaluation, and optional Gemini classification.

**Video link:** Add the hosted recording URL here after recording.

## Assumptions and Trade-offs

- The thresholds and sample outcomes are demo business rules, not legal or production refund advice.
- Dates are evaluated using the backend's current date. The return window is inclusive through day 30; day 31 is too old.
- An amount exactly equal to $500 does not trigger the high-value review rule; the rule is for amounts greater than $500.
- Keyword matching avoids AI calls for common clear reasons, but unusual phrasing may require AI or human review.
- The demo uses SQLite, seeded data, and simple local rules instead of authentication, payment integration, or a production database. The seed command resets mock customer/order data on startup.
- Gemini quota, network availability, and model output can affect classification of ambiguous messages. Policy evaluation remains deterministic, and uncertain cases are escalated rather than auto-approved.

## Publishing

This workspace does not have a GitHub remote configured. After creating a public repository, add it as `origin` and push the assessment source. Keep `.env` and API keys out of the repository.

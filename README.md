# Refund Support

A demo refund-support app with a React customer chat, a Django REST API, seeded mock customers and orders, deterministic policy evaluation, and optional Gemini or OpenAI-compatible assistance.

## Run Locally

Requirements: Docker Engine with the Docker Compose plugin, or Docker Desktop with Compose.

```sh
docker compose up --build
```

The frontend is at <http://localhost:3000>. The API is at <http://localhost:8000/api/>. Compose starts three services: `mock-data` runs migrations and seeds 15 customers and 23 orders, `backend` serves the API from the initialized database, and `frontend` serves the React app after the API is healthy. No AI key is needed to start the app. The legacy command `docker-compose up --build` works with installations that provide the standalone Compose command.

For local backend development without Docker, install the backend dependencies into the active virtual environment before starting Django:

```sh
cd backend
python -m pip install -r requirements.txt
python manage.py runserver
```

To stop the services:

```sh
docker compose down
```

Mock data and refund-request audit records share a named SQLite volume, so they survive normal container restarts and `docker compose down`. The separate seed job is idempotent: it creates or refreshes the 15 sample customers and 23 sample orders without deleting unrelated records. To remove the demo database and seed from scratch, run `docker compose down -v` before starting again.

## Environment Variables

AI is optional. Without a key, deterministic checks and clear locally-classified requests still work. Requests requiring AI classification may be escalated when classification is unavailable.

To configure an AI provider, copy the example file and edit it locally:

```sh
cp .env.example .env
```

Choose one provider, set its key in `.env`, then start or rebuild the backend with `docker compose up --build`. Do not commit `.env` or share API keys. `.env` is ignored by Git.

`.env.example` is intentionally included in the public repository. It contains provider names and blank key fields, not credentials. Reviewers copy it to their own local `.env` and add a key only if they want AI classification; they do not send `.env` to the project author.

| Variable | Default | Purpose |
| --- | --- | --- |
| `AI_PROVIDER` | `gemini` | `gemini` or `openai`. The OpenAI adapter also supports OpenAI-compatible endpoints. |
| `AI_MODEL` | Provider default | Optional model override. Defaults to `gemini-3.8-flash` for Gemini or `gpt-4o-mini` for OpenAI. |
| `GEMINI_API_KEY` | empty | Gemini API key when `AI_PROVIDER=gemini`. |
| `OPENAI_API_KEY` | empty | OpenAI API key when `AI_PROVIDER=openai`. |
| `OPENAI_BASE_URL` | empty | Optional base URL for an OpenAI-compatible API. |
| `AI_REPLY_ENABLED` | `false` | Set to `true` to request AI-written replies after an AI classification. This can use an additional model request; fixed replies are used by default. |

For OpenAI, set `AI_PROVIDER=openai` and `OPENAI_API_KEY=...`. For Gemini, set `AI_PROVIDER=gemini` and `GEMINI_API_KEY=...`. Set `AI_MODEL` only if you want to override that provider's default. The legacy `API_KEY` variable remains accepted as a fallback, but provider-specific key variables are recommended.

## Architecture

- `frontend/`: React and Vite app. The chat supports seeded mock orders and reviewer-authored custom simulations; the support dashboard lists recent decisions.
- `mock-data` Compose service: runs the backend image as a one-shot data initialization job, applying migrations and idempotently seeding the shared SQLite volume.
- `backend/`: Django REST Framework API and policy workflow, reading the same shared SQLite volume after the data job completes.
- `backend/refunds/services/policy.py`: deterministic source of truth for refund outcomes. The model does not override these rules.
- `backend/refunds/services/workflow.py`: request orchestration: sanitization, order lookup, policy pre-checks, optional classification, safeguards, final result, and persisted audit record.
- `backend/refunds/services/ai.py`: optional Gemini/OpenAI-compatible classification and reply generation, local reason matching, prompt-injection checks, and fallback replies.
- `docs/refund-policy.md`: sample business policy matching the implemented decision rules.

Request flow: the chat sends customer email, order ID, and message to `POST /api/refund-request/`. In mock mode, the backend looks up the seeded order. In Custom simulation mode, it evaluates reviewer-supplied order facts without inserting a customer or order into the mock tables. Both paths use the same deterministic policy and return and store `Approved`, `Denied`, or `Escalated`. The support dashboard loads saved outcomes from `GET /api/requests/`; seed customers and orders are provided by `GET /api/customers/`.

Seeded mock data is created automatically when the backend starts. It provides examples and a working default for reviewers; it does not contain canned decisions. The policy engine evaluates the selected order and request each time. Custom simulations let reviewers vary the email, order ID, item, amount, order date, final-sale/refunded flags, and recent-refund count. Simulation facts are not persisted as customer/order records, although the resulting refund-request audit entry is saved.

The policy engine decides the outcome. AI is an assistive classifier/reply writer only, and customer text is treated as untrusted input. Detected injection attempts and conflicting reasons are escalated. AI failures fall back safely rather than changing a policy outcome.

The chat stores an in-flight request and its UUID idempotency key in `sessionStorage`. If a connection drops before confirmation, Retry resends the exact same payload/key; the API returns the original audit record rather than creating a duplicate. The support dashboard records AI status (`success`, `quota_exceeded`, `unavailable`, `not_configured`, or `error`) and warns when recent requests could not use AI. Policy-only/local decisions are labeled separately.

## Policy Summary

The configured return window is 30 days. Final-sale and already-refunded orders are denied; orders belonging to another customer or not found are escalated. Non-final-sale amounts above $500, three or more refunds in the preceding 90 days, unclear reasons, conflicting reasons, and suspected prompt injection require human review. Clear damage, wrong-item, or changed-mind requests for eligible orders may be approved. See [the full sample policy](docs/refund-policy.md).

## Tests

Run the backend tests in the running container:

```sh
docker compose exec backend python manage.py test refunds
```

The tests cover policy boundaries, order ownership, seeded data, local classification, AI-free paths, and prompt-injection/conflicting-request escalation.



## Assumptions and Trade-offs

- The thresholds and sample outcomes are demo business rules, not legal or production refund advice.
- Dates are evaluated using the backend's current date. The return window is inclusive through day 30; day 31 is too old.
- An amount exactly equal to $500 does not trigger the high-value review rule; the rule is for amounts greater than $500.
- Keyword matching avoids AI calls for common clear reasons, but unusual phrasing may require AI or human review.
- The demo uses SQLite, seeded data, and simple local rules instead of authentication, payment integration, or a production database. The separate seed job is idempotent and preserves unrelated customer/order records.
- Provider quota, network availability, and model output can affect classification of ambiguous messages. Policy evaluation remains deterministic, and uncertain cases are escalated rather than auto-approved.

## Publishing

The public source repository is <https://github.com/olakojobukola234/refund-support>. Keep `.env` and API keys out of the repository.

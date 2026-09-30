"""Orchestrates one refund request: cheap rules first, AI only when needed."""
from django.db import IntegrityError

from refunds.models import Customer, Order, RefundRequest
from refunds.services import ai
from refunds.services.policy import Decision, count_recent_refunds, evaluate, pre_check


def _lookup(order_id):
    return Order.objects.select_related("customer").filter(id=order_id).first()


def process_request(customer_email, order_id, message, order_data=None, idempotency_key=None):
    if idempotency_key:
        existing = RefundRequest.objects.filter(idempotency_key=idempotency_key).first()
        if existing:
            return existing

    clean = ai.sanitize(message)
    order_id = (order_id or "").strip().upper()
    classification = ai.classify_locally(clean) if ai.looks_like_injection(clean) else None

    # No order ID given: the AI has to find it in the message.
    if not order_id:
        classification = classification or ai.classify(clean)
        order_id = classification["order_id"] or ""

    if order_data is not None:
        order = Order(
            id=order_id,
            customer=Customer(email=customer_email),
            item=order_data["item"],
            amount=order_data["amount"],
            order_date=order_data["order_date"],
            final_sale=order_data.get("final_sale", False),
            refunded=order_data.get("refunded", False),
        )
        recent_refunds = order_data.get("recent_refunds", 0)
    else:
        order = _lookup(order_id) if order_id else None
        recent_refunds = count_recent_refunds(customer_email)
    decision = pre_check(order, customer_email)

    if decision is None:
        classification = classification or ai.classify_locally(clean) or ai.classify(clean)
        decision = evaluate(order, customer_email, classification["reason"],
                            recent_refunds=recent_refunds)
    elif classification is None:  # decided by rules alone, so no AI call was spent
        classification = {
            "reason": "n/a",
            "injection_suspected": ai.looks_like_injection(clean),
            "conflict_suspected": False,
            "summary": "Decided by policy pre-checks; AI classification skipped.",
            "ai_status": "not_used",
        }

    if classification["injection_suspected"]:
        decision = Decision("Escalated", "INJECTION_REVIEW",
                            ["Message contained instructions aimed at the system; needs human review."])
    elif classification.get("conflict_suspected"):
        decision = Decision("Escalated", "CONFLICTING_REQUEST",
                            ["Request contains conflicting refund reasons; needs human review."])

    ai_status = classification.get("ai_status", "not_used")
    ai_notes = classification["summary"]
    if classification.get("ai_used"):
        reply, reply_ai_status, reply_ai_notes = ai.write_reply_with_status(decision, order)
        if reply_ai_status not in {"success", "not_requested"}:
            ai_status = reply_ai_status
            ai_notes = f"{ai_notes} {reply_ai_notes}".strip()
    else:
        reply = ai.FALLBACKS[decision.status].format(reasons=" ".join(decision.reasons))

    try:
        return RefundRequest.objects.create(
            idempotency_key=idempotency_key,
            customer_email=customer_email,
            order_id=order_id,
            message=clean,
            reason=classification["reason"],
            decision=decision.status,
            rule=decision.rule,
            reasons=decision.reasons,
            injection_flag=classification["injection_suspected"],
            ai_status=ai_status,
            ai_notes=ai_notes,
            reply=reply,
        )
    except IntegrityError:
        if idempotency_key:
            existing = RefundRequest.objects.filter(idempotency_key=idempotency_key).first()
            if existing:
                return existing
        raise
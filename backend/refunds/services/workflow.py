"""Orchestrates one refund request: cheap rules first, AI only when needed."""
from refunds.models import Order, RefundRequest
from refunds.services import ai
from refunds.services.policy import Decision, count_recent_refunds, evaluate, pre_check


def _lookup(order_id):
    return Order.objects.select_related("customer").filter(id=order_id).first()


def process_request(customer_email, order_id, message):
    clean = ai.sanitize(message)
    order_id = (order_id or "").strip().upper()
    classification = ai.classify_locally(clean) if ai.looks_like_injection(clean) else None

    # No order ID given: the AI has to find it in the message.
    if not order_id:
        classification = classification or ai.classify(clean)
        order_id = classification["order_id"] or ""

    order = _lookup(order_id) if order_id else None
    decision = pre_check(order, customer_email)

    if decision is None:
        classification = classification or ai.classify_locally(clean) or ai.classify(clean)
        decision = evaluate(order, customer_email, classification["reason"],
                            recent_refunds=count_recent_refunds(customer_email))
    elif classification is None:  # decided by rules alone, so no AI call was spent
        classification = {
            "reason": "n/a",
            "injection_suspected": ai.looks_like_injection(clean),
            "conflict_suspected": False,
            "summary": "Decided by policy pre-checks; AI classification skipped.",
        }

    if classification["injection_suspected"]:
        decision = Decision("Escalated", "INJECTION_REVIEW",
                            ["Message contained instructions aimed at the system; needs human review."])
    elif classification.get("conflict_suspected"):
        decision = Decision("Escalated", "CONFLICTING_REQUEST",
                            ["Request contains conflicting refund reasons; needs human review."])

    reply = (ai.write_reply(decision, order) if classification.get("ai_used")
             else ai.FALLBACKS[decision.status].format(reasons=" ".join(decision.reasons)))

    return RefundRequest.objects.create(
        customer_email=customer_email,
        order_id=order_id,
        message=clean,
        reason=classification["reason"],
        decision=decision.status,
        rule=decision.rule,
        reasons=decision.reasons,
        injection_flag=classification["injection_suspected"],
        ai_notes=classification["summary"],
        reply=reply,
    )
"""Orchestrates one refund request end to end."""
from refunds.models import Order, RefundRequest
from refunds.services import ai
from refunds.services.policy import Decision, count_recent_refunds, evaluate


def process_request(customer_email, order_id, message):
    clean = ai.sanitize(message)
    classification = ai.classify(clean)

    order_id = (order_id or classification["order_id"] or "").strip().upper()
    order = Order.objects.select_related("customer").filter(id=order_id).first()

    decision = evaluate(
        order, customer_email, classification["reason"],
        recent_refunds=count_recent_refunds(customer_email),
    )

    # Safety net: never auto-approve a request that tried to manipulate the system.
    if classification["injection_suspected"] and decision.status == "Approved":
        decision = Decision(
            "Escalated", "INJECTION_REVIEW",
            ["Message contained instructions aimed at the system; needs human review."],
        )

    reply = ai.write_reply(decision, order)

    record = RefundRequest.objects.create(
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
    return record
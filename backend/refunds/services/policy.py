"""Deterministic refund rules. No AI here: this is the source of truth."""
from dataclasses import dataclass, field
from datetime import date, timedelta

RETURN_WINDOW_DAYS = 30
HUMAN_REVIEW_THRESHOLD = 500
MAX_RECENT_REFUNDS = 3
RECENT_REFUND_DAYS = 90
DEFECT_REASONS = {"damaged", "wrong_item"}
VALID_REASONS = DEFECT_REASONS | {"changed_mind"}


@dataclass
class Decision:
    status: str  # Approved | Denied | Escalated
    rule: str
    reasons: list = field(default_factory=list)


def count_recent_refunds(email, today=None):
    from refunds.models import Order
    since = (today or date.today()) - timedelta(days=RECENT_REFUND_DAYS)
    return Order.objects.filter(customer__email=email, refunded=True,
                                refunded_date__gte=since).count()


def pre_check(order, customer_email, today=None):
    """Checks that don't depend on WHY the customer wants a refund.
    Returns a Decision, or None if the AI must classify the reason first."""
    today = today or date.today()
    if order is None:
        return Decision("Escalated", "ORDER_NOT_FOUND", ["Order was not found."])
    if order.customer.email.lower() != (customer_email or "").lower():
        return Decision("Escalated", "OWNER_MISMATCH", ["Order does not belong to this email."])
    if order.refunded:
        return Decision("Denied", "ALREADY_REFUNDED", ["Order was already refunded."])
    if order.final_sale:
        return Decision("Denied", "FINAL_SALE", ["Final sale items are not refundable."])
    age = (today - order.order_date).days
    if age > RETURN_WINDOW_DAYS:
        return Decision("Denied", "RETURN_WINDOW",
                        [f"Order is {age} days old; window is {RETURN_WINDOW_DAYS} days."])
    if order.amount > HUMAN_REVIEW_THRESHOLD:
        return Decision("Escalated", "HIGH_VALUE",
                        [f"Amount ${order.amount} exceeds ${HUMAN_REVIEW_THRESHOLD}."])
    return None


def evaluate(order, customer_email, reason, recent_refunds=0, today=None):
    early = pre_check(order, customer_email, today)
    if early:
        return early

    is_defect = reason in DEFECT_REASONS
    if recent_refunds >= MAX_RECENT_REFUNDS:
        return Decision("Escalated", "REFUND_PATTERN",
                        [f"{recent_refunds} refunds in the last {RECENT_REFUND_DAYS} days."])
    if reason not in VALID_REASONS:
        return Decision("Escalated", "UNCLEAR_REASON", ["Refund reason is unclear."])
    if order.amount > HUMAN_REVIEW_THRESHOLD:
        return Decision("Escalated", "HIGH_VALUE",
                        [f"Amount ${order.amount} exceeds ${HUMAN_REVIEW_THRESHOLD}."])
    if is_defect:
        return Decision("Approved", "DEFECT_APPROVED", ["Damaged or incorrect item within window."])
    return Decision("Approved", "CHANGE_OF_MIND", ["Eligible item within return window."])
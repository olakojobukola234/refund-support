from rest_framework.decorators import api_view
from rest_framework.response import Response

from refunds.models import RefundRequest
from refunds.serializers import RefundRequestInputSerializer, RefundRequestSerializer
from refunds.services import workflow
from refunds.models import Customer



def _customer_receipt(record):
    status = "Rejected" if record.decision == "Denied" else record.decision
    messages = {
        "Approved": "Your refund request has been approved.",
        "Rejected": "Your request could not be approved. Contact support if you need more information.",
        "Escalated": "Your request needs additional support review.",
    }
    return {
        "request_id": record.id,
        "status": status,
        "message": messages[status],
    }


@api_view(["POST"])
def create_refund_request(request):
    serializer = RefundRequestInputSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    record = workflow.process_request(**serializer.validated_data)
    return Response(_customer_receipt(record), status=201)


@api_view(["GET"])
def get_refund_receipt(request, idempotency_key):
    record = RefundRequest.objects.filter(idempotency_key=idempotency_key).first()
    if record is None:
        return Response({"detail": "Request has not been confirmed yet."}, status=404)
    return Response(_customer_receipt(record))


@api_view(["GET"])
def list_requests(request):
    records = RefundRequest.objects.all()[:100]
    return Response(RefundRequestSerializer(records, many=True).data)



@api_view(["GET"])
def list_customers(request):
    data = []
    for c in Customer.objects.prefetch_related("orders").order_by("name"):
        data.append({
            "id": c.id, "name": c.name, "email": c.email,
            "orders": [
                {"id": o.id, "item": o.item, "amount": str(o.amount),
                 "order_date": o.order_date.isoformat(),
                 "final_sale": o.final_sale, "refunded": o.refunded}
                for o in c.orders.all().order_by("id")
            ],
        })
    return Response(data)
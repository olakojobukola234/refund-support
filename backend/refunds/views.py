from rest_framework.decorators import api_view
from rest_framework.response import Response

from refunds.models import RefundRequest
from refunds.serializers import RefundRequestInputSerializer, RefundRequestSerializer
from refunds.services import workflow
from refunds.models import Customer



@api_view(["POST"])
def create_refund_request(request):
    serializer = RefundRequestInputSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    record = workflow.process_request(**serializer.validated_data)
    return Response({
        "request_id": record.id,
        "status": "received",
        "message": "Your refund request has been received. Contact support if you need an update.",
    }, status=201)


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
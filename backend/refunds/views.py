from rest_framework.decorators import api_view
from rest_framework.response import Response

from refunds.models import RefundRequest
from refunds.serializers import RefundRequestInputSerializer, RefundRequestSerializer
from refunds.services import workflow


@api_view(["POST"])
def create_refund_request(request):
    serializer = RefundRequestInputSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    record = workflow.process_request(**serializer.validated_data)
    return Response(RefundRequestSerializer(record).data, status=201)


@api_view(["GET"])
def list_requests(request):
    records = RefundRequest.objects.all()[:100]
    return Response(RefundRequestSerializer(records, many=True).data)
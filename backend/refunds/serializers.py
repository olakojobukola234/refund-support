from rest_framework import serializers
from refunds.models import RefundRequest


class RefundRequestInputSerializer(serializers.Serializer):
    customer_email = serializers.EmailField()
    order_id = serializers.CharField(max_length=20, required=False, allow_blank=True, default="")
    message = serializers.CharField(max_length=2000)


class RefundRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = RefundRequest
        fields = "__all__"
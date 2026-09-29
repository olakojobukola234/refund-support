from rest_framework import serializers
from refunds.models import RefundRequest


class SimulatedOrderSerializer(serializers.Serializer):
    item = serializers.CharField(max_length=200)
    amount = serializers.DecimalField(max_digits=10, decimal_places=2, min_value=0)
    order_date = serializers.DateField()
    final_sale = serializers.BooleanField(required=False, default=False)
    refunded = serializers.BooleanField(required=False, default=False)
    recent_refunds = serializers.IntegerField(required=False, default=0, min_value=0, max_value=100)


class RefundRequestInputSerializer(serializers.Serializer):
    customer_email = serializers.EmailField()
    order_id = serializers.CharField(max_length=20, required=False, allow_blank=True, default="")
    message = serializers.CharField(max_length=2000)
    order_data = SimulatedOrderSerializer(required=False)

    def validate(self, attrs):
        if attrs.get("order_data") and not attrs.get("order_id", "").strip():
            raise serializers.ValidationError({"order_id": "An order ID is required for a custom simulation."})
        return attrs


class RefundRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = RefundRequest
        fields = "__all__"
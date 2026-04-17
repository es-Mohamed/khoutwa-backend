from rest_framework import serializers
from .models import DailySalesSummary, ProductPerformance
from products.models import Product # Ensure Product model is imported

class DailySalesSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = DailySalesSummary
        fields = '__all__'

# 👇 Add this serializer for Product Movement
class ProductPerformanceSerializer(serializers.ModelSerializer):
    product_name = serializers.SerializerMethodField()
    sku = serializers.SerializerMethodField()

    class Meta:
        model = ProductPerformance
        fields = '__all__'

    def get_product_name(self, obj):
        try:
            return Product.objects.get(id=obj.product_id).name
        except Product.DoesNotExist:
            return "Unknown"

    def get_sku(self, obj):
        try:
            return Product.objects.get(id=obj.product_id).sku
        except Product.DoesNotExist:
            return "-"
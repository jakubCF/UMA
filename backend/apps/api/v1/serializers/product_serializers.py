from rest_framework import serializers
from apps.products.models import Product, ProductVariant, ProductStockAdjustment

class ProductVariantSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductVariant
        fields = '__all__'

class ProductSerializer(serializers.ModelSerializer):
    variants = ProductVariantSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = '__all__'

class ProductStockAdjustmentSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    variant = ProductVariantSerializer(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(),
        source='product',
        required=False,
        write_only=True
    )
    variant_id = serializers.PrimaryKeyRelatedField(
        queryset=ProductVariant.objects.all(),
        source='variant',
        required=False,
        write_only=True
    )

    class Meta:
        model = ProductStockAdjustment
        fields = '__all__'
        read_only_fields = ('status', 'processed_at', 'api_response_data', 'error_message')

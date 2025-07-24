from django.shortcuts import render, get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.viewsets import ModelViewSet
from apps.products.models import Product, ProductVariant, ProductStockAdjustment
from ..serializers.product_serializers import (
    ProductSerializer, 
    ProductVariantSerializer,
    ProductStockAdjustmentSerializer
)

class ProductViewSet(ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    lookup_field = 'code'

    @action(detail=True, methods=['post'])
    def adjust_stock(self, request, code=None):
        product = self.get_object()
        serializer = ProductStockAdjustmentSerializer(data={
            **request.data,
            'product': product.id
        })
        if serializer.is_valid():
            #serializer.save(processed_by=request.user)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ProductVariantViewSet(ModelViewSet):
    queryset = ProductVariant.objects.all()
    serializer_class = ProductVariantSerializer
    lookup_field = 'code'

    @action(detail=True, methods=['post'])
    def adjust_stock(self, request, code=None):
        variant = self.get_object()
        serializer = ProductStockAdjustmentSerializer(data={
            **request.data,
            'variant': variant.id
        })
        if serializer.is_valid():
            #serializer.save(processed_by=request.user)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class StockAdjustmentViewSet(ModelViewSet):
    queryset = ProductStockAdjustment.objects.all()
    serializer_class = ProductStockAdjustmentSerializer

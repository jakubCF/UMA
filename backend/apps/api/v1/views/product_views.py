from django.shortcuts import render, get_object_or_404
from django.db import transaction
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
            'product_id': product.id
        })
        
        if serializer.is_valid():
            # check if stock adjustment for this product already exists and is pending
            existing_adjustment = ProductStockAdjustment.objects.filter(
                product=product,
                status='pending'
            ).first()
            if existing_adjustment:# add adjustment quantity to existing adjustment
                existing_adjustment.adjustment_quantity += serializer.validated_data.get('adjustment_quantity', 0)
                existing_adjustment.save()  # Remove update_fields to allow auto_now to work
                return Response(
                    {"detail": f'Stock adjustment updated. New quantity: {existing_adjustment.adjustment_quantity}'},
                    status=status.HTTP_200_OK
                )
            else:
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
            'variant_id': variant.id
        })
        if serializer.is_valid():
            # check if stock adjustment for this product already exists and is pending
            existing_adjustment = ProductStockAdjustment.objects.filter(
                variant=variant,
                status='pending'
            ).first()
            if existing_adjustment:# add adjustment quantity to existing adjustment
                existing_adjustment.adjustment_quantity += serializer.validated_data.get('adjustment_quantity', 0)
                existing_adjustment.save()  # Remove update_fields to allow auto_now to work
                return Response(
                    {"detail": f'Stock adjustment updated. New quantity: {existing_adjustment.adjustment_quantity}'},
                    status=status.HTTP_200_OK
                )
            else:
                #serializer.save(processed_by=request.user)
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class StockAdjustmentViewSet(ModelViewSet):
    queryset = ProductStockAdjustment.objects.all()
    serializer_class = ProductStockAdjustmentSerializer

    def get_queryset(self):
        queryset = ProductStockAdjustment.objects.all()
        status = self.request.query_params.get('status', None)
        if status is not None:
            queryset = queryset.filter(status=status)
        return queryset
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.status != 'pending':
            return Response(
                {"error": "Only pending adjustments can be deleted."},
                status=status.HTTP_400_BAD_REQUEST
            )
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def create(self, request, *args, **kwargs):
        # Check if request contains multiple adjustments
        adjustments_data = request.data if isinstance(request.data, list) else [request.data]
        processed_data = []
        results = []
        errors = []

        # Pre-process the data to convert codes to IDs
        for adjustment in adjustments_data:
            processed_item = adjustment.copy()
            
            if 'product_code' in adjustment:
                try:
                    product = Product.objects.get(code=adjustment['product_code'])
                    processed_item['product_id'] = product.id
                    del processed_item['product_code']
                except Product.DoesNotExist:
                    return Response(
                        {"error": f"Product with code {adjustment['product_code']} not found"},
                        status=status.HTTP_404_NOT_FOUND
                    )
                    
            if 'variant_code' in adjustment:
                try:
                    variant = ProductVariant.objects.get(code=adjustment['variant_code'])
                    processed_item['variant_id'] = variant.id
                    del processed_item['variant_code']
                except ProductVariant.DoesNotExist:
                    return Response(
                        {"error": f"Variant with code {adjustment['variant_code']} not found"},
                        status=status.HTTP_404_NOT_FOUND
                    )
                    
            processed_data.append(processed_item)
        
        with transaction.atomic():
            for adjustment in processed_data:
                serializer = self.get_serializer(data=adjustment)
                
                if serializer.is_valid():
                    product = serializer.validated_data.get('product')
                    variant = serializer.validated_data.get('variant')
                    
                    filter_kwargs = {'status': 'pending'}
                    if product:
                        filter_kwargs['product'] = product
                    elif variant:
                        filter_kwargs['variant'] = variant
                    
                    existing_adjustment = ProductStockAdjustment.objects.filter(
                        **filter_kwargs
                    ).first()

                    if existing_adjustment:
                        existing_adjustment.adjustment_quantity += serializer.validated_data.get('adjustment_quantity', 0)
                        existing_adjustment.save()  # Remove update_fields to allow auto_now to work
                        results.append({
                            "code": product.code if product else variant.code,
                            "status": "updated",
                            "quantity": existing_adjustment.adjustment_quantity
                        })
                    else:
                        adjustment = serializer.save()
                        results.append({
                            "code": product.code if product else variant.code,
                            "status": "created",
                            "quantity": adjustment.adjustment_quantity
                        })
                else:
                    errors.append({
                        "data": adjustment,
                        "errors": serializer.errors
                    })

        if errors and not results:
            return Response({"errors": errors}, status=status.HTTP_400_BAD_REQUEST)
        
        return Response({
            "results": results,
            "errors": errors
        }, status=status.HTTP_200_OK)

    def perform_create(self, serializer):
        serializer.save()
        #serializer.save(processed_by=self.request.user)
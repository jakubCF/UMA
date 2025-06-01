from django.contrib import admin
from .models import Product, ProductVariant, ProductStockAdjustment

# Register your models here.
admin.site.register(Product)
admin.site.register(ProductVariant)
admin.site.register(ProductStockAdjustment)
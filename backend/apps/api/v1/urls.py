from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import product_views, order_views, upgates_integ_views

router = DefaultRouter()
router.register(r'products', product_views.ProductViewSet)
router.register(r'variants', product_views.ProductVariantViewSet)
router.register(r'stock-adjustments', product_views.StockAdjustmentViewSet)

urlpatterns = [
    # Example: path('', views.product_list, name='product_list'),
    # You'll add your DRF API routes here later
    path('sync/', upgates_integ_views.SyncDataTriggerAPIView.as_view(), name='sync_endpoint'),
    path('orders/', order_views.OrderListCreateView.as_view(), name='order-list-create'),
    path('orders/<int:pk>/', order_views.OrderDetailView.as_view(), name='order-detail'),
    path('orders/<int:order_pk>/items/<int:item_pk>/status/', order_views.OrderItemStatusView.as_view(), name='order-item-status'),
    path('', include(router.urls)),
]
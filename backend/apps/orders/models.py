from django.db import models
from .constants import OrderStatus, OrderItemPickStatus

# Create your models here.
class Order(models.Model):
    order_number = models.CharField(max_length=30, unique=True)
    order_id = models.IntegerField()
    case_number = models.CharField(max_length=30,blank=True, null=True)
    external_order_number = models.CharField(max_length=30,blank=True, null=True)
    uuid = models.CharField(max_length=36,blank=True, null=True)
    language_id = models.CharField(max_length=10,blank=True, null=True)
    currency_id = models.CharField(max_length=10,blank=True, null=True)
    default_currency_rate = models.CharField(max_length=10,blank=True, null=True)
    prices_with_vat_yn = models.BooleanField(blank=True, null=True)
    status_id = models.IntegerField()
    status = models.CharField(max_length=40,blank=True, null=True)
    paid_date = models.DateTimeField(null=True, blank=True)
    tracking_code = models.CharField(max_length=40, null=True, blank=True)
    tracking_url = models.CharField(max_length=200, null=True, blank=True)
    statistics_yn = models.BooleanField(blank=True, null=True)
    resolved_yn = models.BooleanField(blank=True, null=True)
    oss_yn = models.BooleanField(blank=True, null=True)
    internal_note = models.TextField(null=True, blank=True)
    last_update_time = models.DateTimeField(blank=True, null=True)
    creation_time = models.DateTimeField(blank=True, null=True)
    variable_symbol = models.CharField(max_length=20, null=True, blank=True)
    dimensions = models.JSONField(null=True, blank=True)
    total_weight = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    order_total = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    order_total_before_round = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    order_total_rest = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    invoice_number = models.CharField(max_length=30, null=True, blank=True)
    origin = models.CharField(max_length=30, null=True, blank=True)
    admin_url = models.CharField(max_length=200, null=True, blank=True)
    customer = models.JSONField(null=True, blank=True)
    discount_voucher = models.JSONField(null=True, blank=True)
    quantity_discount = models.JSONField(null=True, blank=True)
    loyalty_points = models.JSONField(null=True, blank=True)
    shipment = models.JSONField(null=True, blank=True)
    payment = models.JSONField(null=True, blank=True)
    attachments = models.JSONField(null=True, blank=True)
    metas = models.JSONField(null=True, blank=True)
    pg_status = models.CharField(max_length=30, choices=OrderStatus.CHOICES, default=OrderStatus.PROCESSING)
    pg_created_at = models.DateTimeField(auto_now_add=True)
    pg_updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-creation_time']

    def __str__(self):
        return f"Order {self.order_number} - {self.status}"
    
class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product_id = models.IntegerField(blank=True, null=True)
    options_set_id = models.IntegerField(null=True, blank=True)
    type = models.CharField(max_length=30, null=True, blank=True)
    uuid = models.CharField(max_length=36, null=True, blank=True)
    parent_uuid = models.CharField(max_length=36, null=True, blank=True)
    code = models.CharField(max_length=40, null=True, blank=True)
    code_supplier = models.CharField(max_length=40, null=True, blank=True)
    supplier = models.CharField(max_length=100, null=True, blank=True)
    ean = models.CharField(max_length=100, null=True, blank=True)
    title = models.CharField(max_length=255, null=True, blank=True)
    adult_yn = models.BooleanField(default=False)
    unit = models.CharField(max_length=20, null=True, blank=True)
    length = models.CharField(max_length=20, null=True, blank=True)
    length_unit = models.CharField(max_length=20, null=True, blank=True)
    quantity = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    price_per_unit = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    price_per_unit_with_vat = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    price_per_unit_without_vat = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    price_with_vat = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    price_without_vat = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    vat = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    buy_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    recycling_fee = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    weight = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    availability = models.CharField(max_length=30, null=True, blank=True)
    stock_position = models.CharField(max_length=100, null=True, blank=True)
    invoice_info = models.TextField(null=True, blank=True)
    parameters = models.JSONField(null=True, blank=True)
    configurations = models.JSONField(null=True, blank=True)
    categories = models.JSONField(null=True, blank=True)
    image_url = models.CharField(max_length=200, null=True, blank=True)
    pg_picked = models.CharField(max_length=30, choices=OrderItemPickStatus.CHOICES, default=OrderItemPickStatus.NOT_PICKED, blank=True, null=True)
    pg_created_at = models.DateTimeField(auto_now_add=True)
    pg_updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['order', 'product_id']

    def __str__(self):
        return f"Item {self.title} in Order {self.order.order_number}"
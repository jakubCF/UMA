from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError

class Product(models.Model):
    # CODE from XML (e.g., "P00018") - This is the primary external identifier
    code = models.CharField(max_length=255, unique=True, db_index=True, help_text="Product CODE")

    # Other fields from XML, made optional as per your request
    product_id = models.IntegerField(null=True, blank=True, help_text="Product ID")
    title = models.CharField(max_length=500, blank=True, null=True, help_text="Product title")
    manufacturer = models.CharField(max_length=255, blank=True, null=True)
    ean = models.CharField(max_length=100, blank=True, null=True)
    code_supplier = models.CharField(max_length=255, blank=True, null=True)
    availability_id = models.IntegerField(null=True, blank=True)
    availability = models.CharField(max_length=100, blank=True, null=True)
    stock = models.PositiveIntegerField(default=0)
    stock_position = models.CharField(max_length=100, blank=True, null=True)
    weight = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    unit = models.CharField(max_length=50, blank=True, null=True)
    image_url = models.URLField(max_length=2000, blank=True, null=True) # Main image URL

    # Internal tracking fields
    uma_is_active = models.BooleanField(default=True) # To mark products as inactive if they disappear from feed
    uma_last_synced_at = models.DateTimeField(auto_now=True) # Automatically updates on each save

    class Meta:
        ordering = ['code'] # Default ordering for products

    def __str__(self):
        return f"{self.title or self.code} ({self.code})"

class ProductVariant(models.Model):
    # CODE from XML (e.g., "P00018-9") - This is the primary external identifier for the variant
    code = models.CharField(max_length=255, unique=True, db_index=True, help_text="Variant CODE")

    # Link to the parent Product
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='variants')

    # Other fields from XML, made optional
    variant_id = models.IntegerField(null=True, blank=True, help_text="Variant ID")
    code_supplier = models.CharField(max_length=255, blank=True, null=True)
    ean = models.CharField(max_length=100, blank=True, null=True)
    availability_id = models.IntegerField(null=True, blank=True)
    availability = models.CharField(max_length=100, blank=True, null=True)
    stock = models.PositiveIntegerField(default=0)
    stock_position = models.CharField(max_length=100, blank=True, null=True)
    weight = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    image_url = models.URLField(max_length=2000, blank=True, null=True) # Variant specific image URL

    # Price fields (assuming a single price for simplicity, adjust if multiple pricelists)
    price_original = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    price_with_vat = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    price_without_vat = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    price_purchase = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    currency = models.CharField(max_length=10, blank=True, null=True)

    # Parameters (e.g., Size, Color) - storing as JSONField for flexibility
    parameters = models.JSONField(null=True, blank=True, help_text="JSON of variant parameters (e.g., {'Velikost': '38-41', 'Barva': 'Černá'})")

    # Internal tracking fields
    uma_is_active = models.BooleanField(default=True) # To mark variants as inactive if they disappear from feed
    uma_last_synced_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['product', 'code'] # Order by product, then variant code
        # You might want unique_together for (product, supplier_code) if supplier_code is unique per product
        # unique_together = ('product', 'supplier_code',) # If supplier_code is unique per product

    def __str__(self):
        return f"{self.product.title} - {self.code}"
    
class ProductStockAdjustment(models.Model):
    """
    Records an intended stock adjustment for either a Product (without variants)
    or a specific ProductVariant.
    This model stores the quantity to be added/removed, and tracks the processing status
    with the external Upgates API.
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ]

    # Foreign keys: now one or the other can be set, but not both, and not neither.
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='stock_adjustments',
        null=True, blank=True, # Allow null, as it might be a variant adjustment
        help_text="The product for which stock is being adjusted (if no variants). One of 'product' or 'variant' must be set."
    )
    variant = models.ForeignKey(
        ProductVariant,
        on_delete=models.CASCADE,
        related_name='stock_adjustments',
        null=True, blank=True, # Allow null, as it might be a product adjustment
        help_text="The product variant for which stock is being adjusted (if product has variants). One of 'product' or 'variant' must be set."
    )
    
    adjustment_quantity = models.IntegerField(
        help_text="Quantity to add (positive) or remove (negative) from the current stock."
    )
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        db_index=True,
        help_text="Current status of the stock adjustment process."
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp when the adjustment record was created."
    )
    processed_at = models.DateTimeField(
        null=True, blank=True,
        help_text="Timestamp when the adjustment was last processed by the integration."
    )
    
    processed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, # Links to Django's built-in User model
        on_delete=models.SET_NULL,
        null=True, blank=True,
        help_text="User who initiated this stock adjustment."
    )
    
    api_response_data = models.JSONField(
        null=True, blank=True,
        help_text="Raw API response data from Upgates after attempting update."
    )
    error_message = models.TextField(
        null=True, blank=True,
        help_text="Detailed error message if the API update failed."
    )

    class Meta:
        verbose_name = "Product Stock Adjustment" 
        verbose_name_plural = "Product Stock Adjustments" 
        ordering = ['-created_at'] # Order by most recent adjustments first

    def clean(self):
        """
        Custom validation to ensure exactly one of 'product' or 'variant' is set.
        This runs when form/serializer.is_valid() or instance.full_clean() is called.
        """
        # Check if neither is set
        if not self.product and not self.variant:
            raise ValidationError('Either a product or a variant must be specified for the stock adjustment.')
        
        # Check if both are set
        if self.product and self.variant:
            raise ValidationError('Cannot specify both a product and a variant for the same stock adjustment. Choose one.')
            
        # Optional: You might add more specific validation here.
        # For example, if a variant is chosen, ensure its parent product matches the product field if it was also provided.
        # But the above checks simplify it by forcing selection of only one.

    def save(self, *args, **kwargs):
        """
        Override save to run full_clean if not already done (e.g., when saving directly from code).
        """
        self.full_clean() # Calls clean() and validates other model fields
        super().save(*args, **kwargs)

    def __str__(self):
        target_identifier = "N/A"
        if self.variant:
            target_identifier = f"Variant: {self.variant.code}"
        elif self.product:
            target_identifier = f"Product: {self.product.code}"
        
        return (
            f"Adjustment for {target_identifier}: {self.adjustment_quantity} "
            f"(Status: {self.get_status_display()})"
        )
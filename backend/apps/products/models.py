from django.db import models

class Product(models.Model):
    # CODE from XML (e.g., "P00018") - This is the primary external identifier
    code = models.CharField(max_length=255, unique=True, db_index=True, help_text="Product CODE from external XML")

    # Other fields from XML, made optional as per your request
    product_id = models.IntegerField(null=True, blank=True, help_text="Product ID from external XML")
    title = models.CharField(max_length=500, blank=True, null=True, help_text="Product title (from DESCRIPTIONS/TITLE)")
    manufacturer = models.CharField(max_length=255, blank=True, null=True)
    ean = models.CharField(max_length=100, blank=True, null=True)
    supplier_code = models.CharField(max_length=255, blank=True, null=True)
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
    code = models.CharField(max_length=255, unique=True, db_index=True, help_text="Variant CODE from external XML")

    # Link to the parent Product
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='variants')

    # Other fields from XML, made optional
    variant_id = models.IntegerField(null=True, blank=True, help_text="Variant ID from external XML")
    supplier_code = models.CharField(max_length=255, blank=True, null=True)
    ean = models.CharField(max_length=100, blank=True, null=True)
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
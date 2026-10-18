from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(max_length=255, unique=True)
    icon = models.CharField(max_length=50, default='💊')
    description = models.TextField(null=True, blank=True)
    medicine_count = models.IntegerField(default=0)

    def __str__(self):
        return self.name

class Medicine(models.Model):
    name = models.CharField(max_length=255, db_index=True)
    slug = models.SlugField(max_length=255, unique=True)
    active_salt = models.CharField(max_length=255, db_index=True)
    manufacturer = models.CharField(max_length=255, db_index=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='medicines')
    dosage_form = models.CharField(max_length=100, default='Tablet')
    pack_size_label = models.CharField(max_length=100, default='10 Tablets')
    description = models.TextField(null=True, blank=True)
    uses = models.TextField(null=True, blank=True)
    side_effects = models.TextField(null=True, blank=True)
    is_otc = models.BooleanField(default=False)
    is_prescription = models.BooleanField(default=True)
    dpco_controlled = models.BooleanField(default=False)
    image_url = models.URLField(max_length=1000, null=True, blank=True)
    is_syncing = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Pharmacy(models.Model):
    name = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(max_length=255, unique=True)
    website_url = models.URLField(max_length=1000)
    logo_url = models.URLField(max_length=1000, null=True, blank=True)
    rating = models.FloatField(default=4.0)
    delivery_time = models.CharField(max_length=100, default='1-3 days')
    return_policy = models.CharField(max_length=255, default='7 days return')
    min_order = models.FloatField(default=0)
    free_delivery_above = models.FloatField(default=299)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class Price(models.Model):
    medicine = models.ForeignKey(Medicine, on_delete=models.CASCADE, related_name='prices')
    pharmacy = models.ForeignKey(Pharmacy, on_delete=models.CASCADE, related_name='prices')
    pack_size = models.CharField(max_length=100)
    mrp = models.FloatField()
    selling_price = models.FloatField()
    unit_price = models.FloatField(null=True, blank=True)
    discount_percentage = models.FloatField(default=0)
    in_stock = models.BooleanField(default=True)
    product_url = models.URLField(max_length=2000, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('medicine', 'pharmacy')

    def __str__(self):
        return f"{self.medicine.name} at {self.pharmacy.name}"

class PriceHistory(models.Model):
    medicine = models.ForeignKey(Medicine, on_delete=models.CASCADE)
    pharmacy = models.ForeignKey(Pharmacy, on_delete=models.CASCADE)
    price = models.FloatField()
    recorded_at = models.DateTimeField(auto_now_add=True)

class SavedDrug(models.Model):
    session_id = models.CharField(max_length=255)
    medicine = models.ForeignKey(Medicine, on_delete=models.CASCADE)
    saved_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('session_id', 'medicine')

class AnalyticsClick(models.Model):
    medicine = models.ForeignKey(Medicine, on_delete=models.CASCADE)
    pharmacy = models.ForeignKey(Pharmacy, on_delete=models.CASCADE)
    session_id = models.CharField(max_length=255, null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(null=True, blank=True)
    clicked_at = models.DateTimeField(auto_now_add=True)

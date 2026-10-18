from rest_framework import serializers
from .models import Category, Medicine, Pharmacy, Price

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'icon', 'description', 'medicine_count']

class PharmacySerializer(serializers.ModelSerializer):
    class Meta:
        model = Pharmacy
        fields = ['id', 'name', 'slug', 'website_url', 'logo_url', 'rating', 'delivery_time', 'return_policy', 'free_delivery_above']

class PriceSerializer(serializers.ModelSerializer):
    pharmacy_name = serializers.CharField(source='pharmacy.name', read_only=True)
    pharmacy_slug = serializers.CharField(source='pharmacy.slug', read_only=True)
    pharmacy_logo = serializers.URLField(source='pharmacy.logo_url', read_only=True)
    pharmacy_url = serializers.URLField(source='pharmacy.website_url', read_only=True)
    savings = serializers.SerializerMethodField()

    class Meta:
        model = Price
        fields = ['id', 'pharmacy_id', 'pharmacy_name', 'pharmacy_slug', 'pharmacy_logo', 'pharmacy_url', 'pack_size', 'mrp', 'selling_price', 'unit_price', 'discount_percentage', 'in_stock', 'product_url', 'savings']

    def get_savings(self, obj):
        # This will be populated in the view/context or calculated
        return getattr(obj, 'savings', 0)

class MedicineBasicSerializer(serializers.ModelSerializer):
    category = serializers.CharField(source='category.name', read_only=True, allow_null=True)
    lowest_price = serializers.FloatField(read_only=True)
    highest_price = serializers.FloatField(read_only=True)
    pharmacy_count = serializers.IntegerField(read_only=True)
    has_cheaper_substitute = serializers.BooleanField(read_only=True, default=False)
    cheapest_substitute_price = serializers.FloatField(read_only=True, allow_null=True)

    class Meta:
        model = Medicine
        fields = ['id', 'name', 'slug', 'active_salt', 'manufacturer', 'category', 'dosage_form', 'pack_size_label', 'lowest_price', 'highest_price', 'pharmacy_count', 'has_cheaper_substitute', 'cheapest_substitute_price']

class MedicineDetailSerializer(serializers.ModelSerializer):
    category = serializers.CharField(source='category.name', read_only=True, allow_null=True)
    prices = PriceSerializer(many=True, read_only=True)
    substitutes_count = serializers.IntegerField(read_only=True, default=0)

    class Meta:
        model = Medicine
        fields = ['id', 'name', 'slug', 'active_salt', 'manufacturer', 'category', 'dosage_form', 'pack_size_label', 'description', 'uses', 'side_effects', 'is_otc', 'is_prescription', 'dpco_controlled', 'prices', 'substitutes_count']

class SubstituteSerializer(serializers.ModelSerializer):
    lowest_price = serializers.FloatField(read_only=True)
    price_diff_percentage = serializers.FloatField(read_only=True)

    class Meta:
        model = Medicine
        fields = ['id', 'name', 'slug', 'manufacturer', 'lowest_price', 'price_diff_percentage']

class AutocompleteSerializer(serializers.ModelSerializer):
    category = serializers.CharField(source='category.name', read_only=True, allow_null=True)

    class Meta:
        model = Medicine
        fields = ['id', 'name', 'slug', 'active_salt', 'manufacturer', 'category']

from django.contrib import admin
from .models import Category, Medicine, Pharmacy, Price, PriceHistory, AnalyticsClick

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'medicine_count')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)

@admin.register(Pharmacy)
class PharmacyAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'rating', 'is_active')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)
    list_filter = ('is_active',)

class PriceInline(admin.TabularInline):
    model = Price
    extra = 1

@admin.register(Medicine)
class MedicineAdmin(admin.ModelAdmin):
    list_display = ('name', 'active_salt', 'manufacturer', 'category', 'is_prescription')
    list_filter = ('category', 'is_prescription', 'is_otc')
    search_fields = ('name', 'active_salt', 'manufacturer')
    prepopulated_fields = {'slug': ('name',)}
    inlines = [PriceInline]

@admin.register(Price)
class PriceAdmin(admin.ModelAdmin):
    list_display = ('medicine', 'pharmacy', 'selling_price', 'in_stock')
    list_filter = ('pharmacy', 'in_stock')
    search_fields = ('medicine__name', 'pharmacy__name')

@admin.register(AnalyticsClick)
class AnalyticsClickAdmin(admin.ModelAdmin):
    list_display = ('medicine', 'pharmacy', 'clicked_at', 'ip_address')
    list_filter = ('pharmacy', 'clicked_at')
    readonly_fields = ('medicine', 'pharmacy', 'session_id', 'ip_address', 'user_agent', 'clicked_at')

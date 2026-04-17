from django.contrib import admin
from .models import DailySalesSummary, ProductPerformance, CustomerSegment


@admin.register(DailySalesSummary)
class DailySalesSummaryAdmin(admin.ModelAdmin):
    list_display = ('date', 'total_revenue', 'total_orders', 'total_items_sold')
    ordering = ('-date',)


@admin.register(ProductPerformance)
class ProductPerformanceAdmin(admin.ModelAdmin):
    list_display = ('product_id', 'date', 'revenue', 'units_sold', 'inventory_level')
    list_filter = ('date',)


@admin.register(CustomerSegment)
class CustomerSegmentAdmin(admin.ModelAdmin):
    list_display = ('segment_name', 'created_at', 'updated_at')
    search_fields = ('segment_name',)

from django.contrib import admin
from .models import Category, Product, ProductImage

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'name_ar', 'slug', 'created_at') 
    search_fields = ('name', 'name_ar', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ('created_at', 'updated_at')

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 0
    ordering = ['order']

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'sku', 'category', 'price', 'wholesale_price', 'stock', 'is_featured', 'is_new', 'is_best_seller')
    list_filter = ('category', 'is_featured', 'is_new', 'is_best_seller', 'created_at')
    search_fields = ('name', 'name_ar', 'sku', 'description')
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ('created_at', 'updated_at')
    inlines = [ProductImageInline]

@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ('product', 'order', 'uploaded_at')
    list_filter = ('uploaded_at',)
    search_fields = ('product__name',)
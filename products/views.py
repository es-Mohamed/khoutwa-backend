from rest_framework import viewsets, permissions, parsers
from django_filters import rest_framework as filters
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count

from .models import Category, Product
from .serializers import (
    CategorySerializer, ProductListSerializer, ProductDetailSerializer, ProductWriteSerializer
)

class CategoryViewSet(viewsets.ModelViewSet): # 👈 غيرناها لـ ModelViewSet
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    lookup_field = 'slug'

class ProductFilter(filters.FilterSet):
    # ... (الفلاتر بتاعتك زي ما هي) ...
    category = filters.CharFilter(field_name='category__slug', lookup_expr='exact')
    min_price = filters.NumberFilter(field_name='price', lookup_expr='gte')
    max_price = filters.NumberFilter(field_name='price', lookup_expr='lte')
    name = filters.CharFilter(field_name='name', lookup_expr='icontains')

    class Meta:
        model = Product
        fields = ['category', 'min_price', 'max_price', 'name', 'is_featured']

class ProductViewSet(viewsets.ModelViewSet): # 👈 غيرناها لـ ModelViewSet
    queryset = Product.objects.all().select_related('category').prefetch_related('images')
    filter_backends = [DjangoFilterBackend]
    filterset_class = ProductFilter
    lookup_field = 'slug' 
    
    # 👈 بنقول لجانجو إحنا هنستقبل ملفات (صور) مع الداتا
    parser_classes = [parsers.MultiPartParser, parsers.FormParser, parsers.JSONParser]

    def get_permissions(self):
        # 👈 أي حد يقدر يشوف المنتجات، بس الإدمن بس هو اللي يضيف أو يعدل
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [permissions.IsAdminUser()]
        return [permissions.AllowAny()]

    def get_queryset(self):
        qs = super().get_queryset()
        # السطر ده بيجيب العدد كله في خطوة واحدة من الداتابيز
        qs = qs.annotate(wishlist_count_annotated=Count('wishlisted_by'))
        return qs.order_by('-created_at')

    def get_serializer_class(self):
        # 👈 بنحدد المفتش (Serializer) المناسب حسب نوع الطلب
        if self.action in ['create', 'update', 'partial_update']:
            return ProductWriteSerializer
        if self.action == 'retrieve':
            return ProductDetailSerializer
        return ProductListSerializer
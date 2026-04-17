from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SalesAnalyticsViewSet, ProductPerformanceViewSet # 👈 Import the new ViewSet

router = DefaultRouter()
router.register(r'sales', SalesAnalyticsViewSet, basename='sales-analytics')
# 👇 Register the product performance endpoint
router.register(r'products-movement', ProductPerformanceViewSet, basename='products-movement')

urlpatterns = [
    path('', include(router.urls)),
]
from django.utils import timezone
from datetime import timedelta
from django.db.models import Sum
from django.db.models.functions import TruncMonth, TruncYear
from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import DailySalesSummary, ProductPerformance
from .serializers import DailySalesSummarySerializer, ProductPerformanceSerializer

class SalesAnalyticsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = DailySalesSummary.objects.all().order_by('-date')
    serializer_class = DailySalesSummarySerializer
    permission_classes = [permissions.IsAdminUser]

    # 1. المبيعات الشهرية (ترجع مبيعات كل يوم لآخر 30 يوم)
    @action(detail=False, methods=['get'])
    def monthly_chart(self, request):
        thirty_days_ago = timezone.now().date() - timedelta(days=30)
        daily_stats = DailySalesSummary.objects.filter(date__gte=thirty_days_ago).order_by('date')
        
        data = [
            {
                'date': stat.date.strftime('%Y-%m-%d'), # بنبعت التاريخ باليوم
                'revenue': stat.total_revenue,
                'orders': stat.total_orders,
                'items': stat.total_items_sold
            } for stat in daily_stats
        ]
        return Response(data)

    # 2. المبيعات السنوية (ترجع مبيعات كل شهر في السنة الحالية)
    @action(detail=False, methods=['get'])
    def yearly_chart(self, request):
        current_year = timezone.now().year
        monthly_stats = DailySalesSummary.objects.filter(date__year=current_year)\
            .annotate(month=TruncMonth('date'))\
            .values('month')\
            .annotate(
                revenue=Sum('total_revenue'),
                orders=Sum('total_orders'),
                items=Sum('total_items_sold')
            ).order_by('month')
            
        data = [
            {
                'month': stat['month'].strftime('%Y-%m-01'), # بنبعت التاريخ بالشهر
                'revenue': stat['revenue'],
                'orders': stat['orders']
            } for stat in monthly_stats
        ]
        return Response(data)

# 👇 Add this ViewSet for Product Movement
class ProductPerformanceViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for tracking product movement, inventory levels, and top sellers.
    """
    queryset = ProductPerformance.objects.all().order_by('-date', '-revenue')
    serializer_class = ProductPerformanceSerializer
    permission_classes = [permissions.IsAdminUser]

    @action(detail=False, methods=['get'])
    def top_sellers(self, request):
        """
        Returns the top 10 best-selling products across all time.
        Useful for the Dashboard Top Products chart.
        """
        # Aggregate total units sold and revenue per product
        top_products = ProductPerformance.objects.values('product_id').annotate(
            total_units_sold=Sum('units_sold'),
            total_revenue=Sum('revenue')
        ).order_by('-total_units_sold')[:10]

        # Enhance data with product names for the frontend
        from products.models import Product
        results = []
        for item in top_products:
            try:
                product = Product.objects.get(id=item['product_id'])
                item['product_name'] = product.name
                item['stock_left'] = product.stock
            except Product.DoesNotExist:
                item['product_name'] = "Deleted Product"
                item['stock_left'] = 0
            results.append(item)

        return Response(results)
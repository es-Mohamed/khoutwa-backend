from datetime import timedelta
from django.utils import timezone
from django.core.management.base import BaseCommand
from django.db.models import Sum, F, Count
from analytics.models import DailySalesSummary, ProductPerformance
from orders.models import Order, OrderItem
from products.models import Product

class Command(BaseCommand):
    help = 'Run the daily analytics pipeline (Optimized ORM Way)'

    def handle(self, *args, **options):
        # yesterday = timezone.now().date() - timedelta(days=1)
        yesterday = timezone.now().date()
        self.stdout.write(f'Running pipeline for date: {yesterday}')

        # 1. summarize daily sales
        daily_stats = Order.objects.filter(status='delivered', created_at__date=yesterday).aggregate(
            total_revenue=Sum('total_amount'), total_orders=Count('id')
        )
        items_stats = OrderItem.objects.filter(order__status='delivered', order__created_at__date=yesterday).aggregate(
            total_items=Sum('quantity')
        )

        if daily_stats['total_orders'] > 0:
            DailySalesSummary.objects.update_or_create(
                date=yesterday,
                defaults={
                    'total_revenue': daily_stats['total_revenue'] or 0,
                    'total_orders': daily_stats['total_orders'] or 0,
                    'total_items_sold': items_stats['total_items'] or 0,
                }
            )

        # 2. أداء المنتجات
        products_sold = OrderItem.objects.filter(
            order__status='delivered', order__created_at__date=yesterday
        ).values('product_id').annotate(
            units_sold=Sum('quantity'), revenue=Sum(F('quantity') * F('price'))
        )

        product_ids = [item['product_id'] for item in products_sold]
        current_stocks = dict(Product.objects.filter(id__in=product_ids).values_list('id', 'stock'))

        performance_records = [
            ProductPerformance(
                product_id=item['product_id'], date=yesterday,
                revenue=item['revenue'], units_sold=item['units_sold'],
                inventory_level=current_stocks.get(item['product_id'], 0)
            ) for item in products_sold
        ]

        if performance_records:
            ProductPerformance.objects.bulk_create(
                performance_records, update_conflicts=True,
                unique_fields=['product_id', 'date'], update_fields=['revenue', 'units_sold', 'inventory_level']
            )

        self.stdout.write(self.style.SUCCESS('Pipeline executed successfully! 🚀'))
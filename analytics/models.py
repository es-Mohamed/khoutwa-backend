from django.db import models


class DailySalesSummary(models.Model):
    date = models.DateField()
    total_revenue = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    total_orders = models.IntegerField(default=0)
    total_items_sold = models.IntegerField(default=0)

    class Meta:
        ordering = ['-date']
        unique_together = ('date',)

    def __str__(self):
        return f"DailySalesSummary({self.date})"


class ProductPerformance(models.Model):
    product_id = models.IntegerField()
    date = models.DateField()
    revenue = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    units_sold = models.IntegerField(default=0)
    inventory_level = models.IntegerField(default=0)

    class Meta:
        ordering = ['-date']
        unique_together = ('product_id', 'date')

    def __str__(self):
        return f"ProductPerformance(product_id={self.product_id}, date={self.date})"


class CustomerSegment(models.Model):
    segment_name = models.CharField(max_length=120)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ['segment_name']

    def __str__(self):
        return self.segment_name

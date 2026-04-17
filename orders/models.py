from django.db import models
from django.core.validators import MinValueValidator


class Cart(models.Model):
    """Shopping cart model."""
    user = models.OneToOneField('accounts.User', on_delete=models.CASCADE, related_name='cart')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']

    def __str__(self):
        return f'Cart of {self.user.email}'

    @property
    def total_items(self):
        """Total number of items in cart."""
        return self.items.aggregate(
            total=models.Sum('quantity')
        )['total'] or 0

    @property
    def total_price(self):
        """Total price of all items in cart."""
        return sum(item.subtotal for item in self.items.all())


class CartItem(models.Model):
    """Items in shopping cart."""
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey('products.Product', on_delete=models.CASCADE)
    
    # 👈 ضفنا الحقول هنا عشان الداتابيز تقبلها من الـ views
    size = models.CharField(max_length=50, null=True, blank=True)
    color = models.CharField(max_length=50, null=True, blank=True)
    is_wholesale = models.BooleanField(default=False)
    
    quantity = models.IntegerField(validators=[MinValueValidator(1)])

    class Meta:
        # 👈 عدلنا دي عشان نسمح للعميل يطلب نفس المنتج لو المقاس أو اللون مختلف
        unique_together = ('cart', 'product', 'size', 'color', 'is_wholesale')

    def __str__(self):
        return f'{self.quantity}x {self.product.name} in {self.cart.user.email}\'s cart'

    @property
    def subtotal(self):
        """Calculate subtotal for this item."""
        if self.is_wholesale:
            # لو جملة، نضرب سعر قطعة الجملة × 10 (الدستة) × الكمية المطلوبة
            wholesale_price = self.product.wholesale_price or 0
            return wholesale_price * 10 * self.quantity
        
        # لو قطاعي، نحسب بالسعر العادي
        return self.product.price * self.quantity


class Order(models.Model):
    """Order model."""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
        ('refunded', 'Refunded'),
    ]

    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]

    user = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='orders')
    order_number = models.CharField(max_length=50, unique=True)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)
    shipping_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    shipping_address = models.TextField()
    billing_address = models.TextField(null=True, blank=True)
    notes = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    shipped_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['order_number']),
            models.Index(fields=['user']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f'Order {self.order_number} by {self.user.email}'

    @property
    def final_amount(self):
        """Calculate final amount with all charges."""
        return self.total_amount + self.shipping_cost + self.tax_amount - self.discount_amount


class OrderItem(models.Model):
    """Items in an order."""
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey('products.Product', on_delete=models.CASCADE)
    
    # 👈 رجعنا تفاصيل المتغيرات هنا عشان نعرف العميل طلب إيه بالظبط
    size = models.CharField(max_length=50, null=True, blank=True)
    color = models.CharField(max_length=50, null=True, blank=True)
    is_wholesale = models.BooleanField(default=False) # عشان لو طلب جملة
    
    quantity = models.IntegerField(validators=[MinValueValidator(1)])
    price = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f'{self.product.name} in Order {self.order.order_number}'

    @property
    def subtotal(self):
        """Calculate subtotal for this order item."""
        return self.price * self.quantity


class Payment(models.Model):
    """Payment model for orders."""
    PAYMENT_METHOD_CHOICES = [
        ('card', 'Credit/Debit Card'),
        ('bank_transfer', 'Bank Transfer'),
        ('wallet', 'Digital Wallet'),
        ('cod', 'Cash on Delivery'),
    ]

    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='payment')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    
    transaction_id = models.CharField(max_length=100, unique=True, null=True, blank=True)
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ], default='pending')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'Payment for Order {self.order.order_number}'


class Wishlist(models.Model):
    """User wishlist model."""
    user = models.OneToOneField('accounts.User', on_delete=models.CASCADE, related_name='wishlist')
    products = models.ManyToManyField('products.Product', related_name='wishlisted_by')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'Wishlist of {self.user.email}'
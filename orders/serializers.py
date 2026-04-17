from rest_framework import serializers
from .models import Cart, CartItem, Order, OrderItem, Payment, Wishlist

class CartItemSerializer(serializers.ModelSerializer):
    """Serializer for CartItem model."""
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_name_ar = serializers.CharField(source='product.name_ar', read_only=True)
    product_image = serializers.SerializerMethodField()
    price = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        # 👇 ضفنا المقاس واللون وشيلنا variant
        fields = ('id', 'product', 'product_name', 'product_name_ar', 'product_image', 'size', 'color', 'is_wholesale', 'quantity', 'price', 'subtotal')

    def get_product_image(self, obj):
        image = obj.product.images.first()
        return image.url if image else None
    
    # 👈 الدالة الجديدة اللي بتبعت السعر الصح للفرونت إند
    def get_price(self, obj):
        if obj.is_wholesale:
            wholesale_price = obj.product.wholesale_price or 0
            return wholesale_price * 10
        return obj.product.price

class CartSerializer(serializers.ModelSerializer):
    """Serializer for Cart model."""
    items = CartItemSerializer(many=True, read_only=True)
    total_items = serializers.IntegerField(read_only=True)
    total_price = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)

    class Meta:
        model = Cart
        fields = ('id', 'items', 'total_items', 'total_price', 'updated_at')

class OrderItemSerializer(serializers.ModelSerializer):
    """Serializer for OrderItem model."""
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_name_ar = serializers.CharField(source='product.name_ar', read_only=True)
    product_image = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = ('id', 'product', 'product_name', 'product_name_ar', 'product_image', 'size', 'color', 'is_wholesale', 'quantity', 'price', 'subtotal')

    def get_product_image(self, obj):
        image = obj.product.images.first()
        return image.url if image else None

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ('id', 'payment_method', 'amount', 'transaction_id', 'status', 'created_at')

class OrderSerializer(serializers.ModelSerializer):
    """Serializer for Order model."""
    items = OrderItemSerializer(many=True, read_only=True)
    payment = PaymentSerializer(read_only=True)
    final_amount = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    
    # 👈 1. غيرنا الأسماء لـ customer عشان تطابق الفرونت إند بالظبط
    # 👈 2. استخدمنا MethodField عشان نحمي الكود من أي نقص في بيانات العميل
    customer_name = serializers.SerializerMethodField()
    customer_email = serializers.CharField(source='user.email', read_only=True)
    customer_phone = serializers.SerializerMethodField()

    class Meta:
        model = Order
        # ضفنا الأسماء الجديدة هنا
        fields = ('id', 'order_number', 'user', 'customer_name', 'customer_email', 'customer_phone', 
                  'status', 'payment_status', 'total_amount', 'shipping_cost', 'tax_amount', 
                  'discount_amount', 'final_amount', 'items', 'payment', 'shipping_address', 
                  'notes', 'created_at', 'updated_at')
        read_only_fields = ('id', 'order_number', 'status', 'payment_status', 'total_amount', 'final_amount', 'created_at', 'updated_at')

    # 🛡️ دالة ذكية لجلب الاسم (حتى لو العميل مسجل بطريقة مختلفة)
    def get_customer_name(self, obj):
        if not obj.user:
            return "زائر"
        name = getattr(obj.user, 'name', '')
        if not name: # لو حقل name فاضي، نجمع الاسم الأول والأخير
            name = f"{getattr(obj.user, 'first_name', '')} {getattr(obj.user, 'last_name', '')}".strip()
        return name if name else "عميل"

    # 🛡️ دالة ذكية لجلب رقم التليفون (حتى لو الحقل اسمه phone أو phone_number)
    def get_customer_phone(self, obj):
        if not obj.user:
            return "غير متوفر"
        return getattr(obj.user, 'phone_number', getattr(obj.user, 'phone', 'غير متوفر'))

class WishlistSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wishlist
        fields = ('id', 'products', 'updated_at')
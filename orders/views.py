import uuid
from decimal import Decimal, InvalidOperation
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Cart, CartItem, Order, OrderItem, Wishlist
from .serializers import CartSerializer, OrderSerializer, WishlistSerializer

class CartViewSet(viewsets.ViewSet):
    """ViewSet for shopping cart."""
    permission_classes = [IsAuthenticated]

    def list(self, request):
        cart, _ = Cart.objects.get_or_create(user=request.user)
        serializer = CartSerializer(cart)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def add_item(self, request):
        cart, _ = Cart.objects.get_or_create(user=request.user)
        product_id = request.data.get('product_id')
        quantity = int(request.data.get('quantity', 1))
        
        # 👈 بنستقبل التفاصيل الجديدة
        size = request.data.get('size')
        color = request.data.get('color')
        is_wholesale = request.data.get('is_wholesale', False)

        item, created = CartItem.objects.get_or_create(
            cart=cart,
            product_id=product_id,
            size=size,
            color=color,
            is_wholesale=is_wholesale,
            defaults={'quantity': quantity}
        )

        if not created:
            item.quantity += quantity
            item.save()

        serializer = CartSerializer(cart)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def remove_item(self, request):
        cart_item_id = request.data.get('cart_item_id')
        try:
            cart_item = CartItem.objects.get(id=cart_item_id, cart__user=request.user)
            cart_item.delete()
            cart = request.user.cart
            serializer = CartSerializer(cart)
            return Response(serializer.data)
        except CartItem.DoesNotExist:
            return Response({'error': 'Cart item not found'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['post'])
    def clear(self, request):
        cart, _ = Cart.objects.get_or_create(user=request.user)
        cart.items.all().delete()
        serializer = CartSerializer(cart)
        return Response(serializer.data)

    
    @action(detail=False, methods=['post'])
    def sync(self, request):
        """مزامنة السلة المحلية مع سلة قاعدة البيانات"""
        cart, _ = Cart.objects.get_or_create(user=request.user)
        
        # بنستقبل المصفوفة اللي جاية من الفرونت إند
        local_items = request.data.get('local_items', [])

        # بنلف على كل منتج في السلة الوهمية وندمجه
        for item_data in local_items:
            product_id = item_data.get('product_id')
            quantity = int(item_data.get('quantity', 1))
            size = item_data.get('size')
            color = item_data.get('color')
            is_wholesale = item_data.get('is_wholesale', False)

            if not product_id:
                continue

            # استخدام نفس اللوجيك الذكي بتاعنا
            item, created = CartItem.objects.get_or_create(
                cart=cart,
                product_id=product_id,
                size=size,
                color=color,
                is_wholesale=is_wholesale,
                defaults={'quantity': quantity}
            )

            if not created:
                # لو المنتج موجود، نجمع الكمية (قاعدة الجمع)
                item.quantity += quantity
                item.save()

        # في النهاية بنرجع السلة المدمجة بالكامل
        serializer = CartSerializer(cart)
        return Response(serializer.data, status=status.HTTP_200_OK)


class OrderViewSet(viewsets.ModelViewSet): # 👈 غيرناها لـ ModelViewSet عشان نسمح بإنشاء طلب
    """ViewSet for orders."""
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # الإدمن يشوف كل الطلبات، اليوزر العادي يشوف طلباته بس
        if self.request.user.is_superuser or self.request.user.role == 'admin':
            return Order.objects.all().order_by('-created_at')
        return Order.objects.filter(user=self.request.user).order_by('-created_at')

    def create(self, request, *args, **kwargs):
        """تحويل السلة إلى طلب فعلي"""
        user = request.user
        cart = getattr(user, 'cart', None)

        # 1. التأكد إن السلة مش فاضية
        if not cart or cart.items.count() == 0:
            return Response({"error": "سلة التسوق فارغة"}, status=status.HTTP_400_BAD_REQUEST)

        # 1. استلام وتأمين عنوان الشحن (التأكد إنه مش فاضي)
        shipping_address = request.data.get('shipping_address', '').strip()
        if not shipping_address:
            return Response({"error": "عنوان الشحن مطلوب لإتمام الطلب"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            raw_shipping_cost = request.data.get('shipping_cost', 0)
            shipping_cost = Decimal(str(raw_shipping_cost))
            if shipping_cost < 0:
                shipping_cost = Decimal('0') # لو بعت رقم سالب، نرجعه صفر
        except (ValueError, TypeError, InvalidOperation):
            shipping_cost = Decimal('0') # لو بعت حروف بدل الأرقام، نرجعه صفر
            
        notes = request.data.get('notes', '')

        # 2. إنشاء رقم طلب فريد
        order_number = f"ORD-{uuid.uuid4().hex[:8].upper()}"
        
        # 3. إنشاء الطلب الأساسي
        order = Order.objects.create(
            user=user,
            order_number=order_number,
            total_amount=cart.total_price+ shipping_cost,
            shipping_cost=shipping_cost,
            shipping_address=shipping_address,
            notes=notes
        )

        # 4. نقل المنتجات من السلة للطلب (مع السعر اللي العميل اشترى بيه عشان لو السعر اتغير بعدين)
        for cart_item in cart.items.all():
            # 👈 السعر هنا هيكون مضروب في 10 لو هو جملة
            if cart_item.is_wholesale:
                item_price = (cart_item.product.wholesale_price or 0) * 10
            else:
                item_price = cart_item.product.price
            
            OrderItem.objects.create(
                order=order,
                product=cart_item.product,
                size=cart_item.size,
                color=cart_item.color,
                is_wholesale=cart_item.is_wholesale,
                quantity=cart_item.quantity,
                price=item_price 
            )

        # 5. تفريغ السلة بعد نجاح الطلب
        cart.items.all().delete()

        serializer = self.get_serializer(order)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    # 👈 الدالة دي معمولة مخصوص للأدمن عشان يغير حالة الطلب بطلقة
    @action(detail=True, methods=['patch', 'post'])
    def update_status(self, request, pk=None):
        # التأكد إن اللي بيعدل ده أدمن
        if not (request.user.is_superuser or request.user.role == 'admin'):
            return Response({'error': 'غير مصرح لك'}, status=status.HTTP_403_FORBIDDEN)
            
        order = self.get_object()
        new_status = request.data.get('status')
        
        if new_status:
            order.status = new_status
            order.save()
            return Response({'status': 'success', 'new_status': order.status})
            
        return Response({'error': 'يجب تحديد الحالة الجديدة'}, status=status.HTTP_400_BAD_REQUEST)


class WishlistViewSet(viewsets.ViewSet):
    """ViewSet for wishlist."""

    permission_classes = [IsAuthenticated]

    def list(self, request):
        """Get user's wishlist."""
        wishlist, _ = Wishlist.objects.get_or_create(user=request.user)
        serializer = WishlistSerializer(wishlist)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def add_product(self, request):
        """Add product to wishlist."""
        wishlist, _ = Wishlist.objects.get_or_create(user=request.user)
        product_id = request.data.get('product_id')
        wishlist.products.add(product_id)
        serializer = WishlistSerializer(wishlist)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def remove_product(self, request):
        """Remove product from wishlist."""
        wishlist, _ = Wishlist.objects.get_or_create(user=request.user)
        product_id = request.data.get('product_id')
        wishlist.products.remove(product_id)
        serializer = WishlistSerializer(wishlist)
        return Response(serializer.data)

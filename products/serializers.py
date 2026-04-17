from rest_framework import serializers
from .models import Category, Product, ProductImage
import json

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'name_ar', 'slug', 'image']

class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['id', 'url', 'alt_text', 'order']

class ProductListSerializer(serializers.ModelSerializer):
    main_image = serializers.SerializerMethodField()
    category = serializers.SlugRelatedField(slug_field='slug', read_only=True)
    # الفرونت إند بيستنى inStock
    inStock = serializers.BooleanField(source='in_stock', read_only=True)
    wholesalePrice = serializers.DecimalField(source='wholesale_price', max_digits=12, decimal_places=2, read_only=True)
    wishlist_count = serializers.IntegerField(source='wishlisted_by.count', read_only=True)

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'name_ar', 'slug', 'category', 'price',
            'wholesalePrice', 'main_image', 'is_new', 'is_best_seller',
            'is_featured', 'stock', 'inStock','sku', 'description', 'description_ar',
            'wishlist_count']

    def get_main_image(self, obj):
        first_image = obj.images.first()
        if first_image:
            return first_image.url
        return None

class ProductDetailSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, read_only=True)
    category = serializers.SlugRelatedField(slug_field='slug', read_only=True)
    inStock = serializers.BooleanField(source='in_stock', read_only=True)
    wholesalePrice = serializers.DecimalField(source='wholesale_price', max_digits=12, decimal_places=2, read_only=True)

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'name_ar', 'slug', 'category', 'price',
            'wholesalePrice', 'colors', 'sizes', 'description',
            'description_ar', 'images', 'is_new', 'is_best_seller',
            'is_featured', 'stock', 'inStock', 'sku'
        ]

class ProductWriteSerializer(serializers.ModelSerializer):
    """Serializer مخصص لإنشاء وتعديل المنتجات واستقبال الصور"""
    uploaded_images = serializers.ListField(
        child=serializers.ImageField(allow_empty_file=False, use_url=False),
        write_only=True,
        required=False
    )
    # بنسمح باستقبال اسم القسم (slug) عشان نربطه بالمنتج
    category_slug = serializers.SlugRelatedField(
        queryset=Category.objects.all(), slug_field='slug', source='category', write_only=True
    )

    class Meta:
        model = Product
        fields = [
            'name', 'name_ar', 'category_slug', 'price', 'wholesale_price', 
            'stock', 'description', 'description_ar', 'is_new', 'is_best_seller', 
            'is_featured', 'uploaded_images', 'colors', 'sizes'
        ]

    def create(self, validated_data):
        uploaded_images = validated_data.pop('uploaded_images', [])
        
        # تحويل الألوان والمقاسات من String لـ JSON لو مبعوتة كـ String في الـ FormData
        if 'colors' in validated_data and isinstance(validated_data['colors'], str):
            validated_data['colors'] = json.loads(validated_data['colors'])
        if 'sizes' in validated_data and isinstance(validated_data['sizes'], str):
            validated_data['sizes'] = json.loads(validated_data['sizes'])

        product = Product.objects.create(**validated_data)
        
        # حفظ الصور في جدول ProductImage
        for index, image in enumerate(uploaded_images):
            ProductImage.objects.create(product=product, image=image, order=index)
            
        return product

    def update(self, instance, validated_data):
        uploaded_images = validated_data.pop('uploaded_images', [])
        
        if 'colors' in validated_data and isinstance(validated_data['colors'], str):
            validated_data['colors'] = json.loads(validated_data['colors'])
        if 'sizes' in validated_data and isinstance(validated_data['sizes'], str):
            validated_data['sizes'] = json.loads(validated_data['sizes'])

        # تحديث بيانات المنتج
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # لو في صور جديدة، ممكن نمسح القديم ونضيف الجديد (أو حسب المنطق بتاعك)
        if uploaded_images:
            instance.images.all().delete()
            for index, image in enumerate(uploaded_images):
                ProductImage.objects.create(product=instance, image=image, order=index)

        return instance
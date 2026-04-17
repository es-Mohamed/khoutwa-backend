"""Products models tailored to the React frontend mock shape.

The frontend expects each product to expose:
- id (string slug)
- name, nameAr
- price and wholesale price
- images: array of image URLs
- colors: array of objects { name, nameAr, hex }
- sizes: array of integers
- description, descriptionAr
- inStock boolean

This module provides models that store the canonical data and a
small gallery model for multiple images.
"""

from django.db import models
from django.utils.text import slugify
from django.core.validators import MinValueValidator


class Category(models.Model):
    """Product category used by the frontend (e.g. 'leather', 'sneakers')."""
    name = models.CharField(max_length=255, unique=True)
    name_ar = models.CharField(max_length=255, blank=True) # الحقل الجديد للعربي
    slug = models.SlugField(max_length=255, unique=True)
    image = models.ImageField(upload_to='categories/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'

    def __str__(self) -> str:
        return self.name


class Product(models.Model):
    """Core product model matching the frontend mock structure.

    The frontend refers to products by a string `id` (for example
    "leather-oxford-1"). We surface that as the `slug` field and
    serialize it as `id` to keep compatibility.
    """

    name = models.CharField(max_length=255)
    name_ar = models.CharField(max_length=255, blank=True)
    slug = models.SlugField(max_length=255, unique=True)

    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='products')

    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    wholesale_price = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0)], default=0)

    # Store colors and sizes as JSON to match the flexible frontend structure.
    # colors: [{ name, nameAr, hex }, ...]
    colors = models.JSONField(default=list, blank=True)
    # sizes: [40,41,42,...]
    sizes = models.JSONField(default=list, blank=True)

    is_new = models.BooleanField(default=False)
    is_best_seller = models.BooleanField(default=False)
    is_featured = models.BooleanField(default=False)

    description = models.TextField(blank=True)
    description_ar = models.TextField(blank=True)

    stock = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    sku = models.CharField(max_length=100, unique=True, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['sku']),
            models.Index(fields=['category']),
            models.Index(fields=['is_featured']),
        ]

    def __str__(self) -> str:
        return self.name

    def save(self, *args, **kwargs):
        # Ensure slug exists for frontend ids; allow explicit slug but
        # auto-generate from name if missing.
        if not self.slug:
            base = slugify(self.name)[:200]
            slug = base
            counter = 1
            while Product.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base}-{counter}"
                counter += 1
            self.slug = slug

        super().save(*args, **kwargs)

    @property
    def in_stock(self) -> bool:
        return self.stock > 0


class ProductImage(models.Model):
    """Additional images for a product (gallery). The first image is the main image.

    Storing an `order` allows deterministic ordering for the frontend gallery.
    """

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='products/')
    alt_text = models.CharField(max_length=255, blank=True)
    order = models.PositiveIntegerField(default=0)

    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', 'uploaded_at']

    def __str__(self) -> str:
        return f"{self.product.name} - image #{self.order}"

    @property
    def url(self) -> str:
        try:
            return self.image.url
        except Exception:
            return ''

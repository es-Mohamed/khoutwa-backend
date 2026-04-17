from django.db import models


class BaseModel(models.Model):
    """Abstract base model with common fields."""

    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class SiteSettings(models.Model):
    """Global site settings model."""

    site_name = models.CharField(max_length=255, default='Khoutwa')
    site_description = models.TextField(blank=True)
    site_logo = models.ImageField(upload_to='settings/', null=True, blank=True)
    site_favicon = models.ImageField(upload_to='settings/', null=True, blank=True)
    
    phone_number = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    address = models.TextField(blank=True)
    
    facebook_url = models.URLField(blank=True)
    twitter_url = models.URLField(blank=True)
    instagram_url = models.URLField(blank=True)
    linkedin_url = models.URLField(blank=True)
    
    maintenance_mode = models.BooleanField(default=False)
    
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Site Settings'
        verbose_name_plural = 'Site Settings'

    def __str__(self):
        return self.site_name


class Notification(models.Model):
    """Notification model for user communications."""

    NOTIFICATION_TYPES = [
        ('order', 'Order Update'),
        ('promotion', 'Promotion'),
        ('account', 'Account Update'),
        ('product', 'Product Update'),
    ]

    user = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    title = models.CharField(max_length=255)
    message = models.TextField()
    
    is_read = models.BooleanField(default=False)
    link = models.URLField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.title} - {self.user.email}'


class ContactMessage(models.Model):
    """Contact form submissions."""

    name = models.CharField(max_length=255)
    email = models.EmailField()
    subject = models.CharField(max_length=255)
    message = models.TextField()
    
    is_read = models.BooleanField(default=False)
    response = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    responded_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.subject} - {self.name}'

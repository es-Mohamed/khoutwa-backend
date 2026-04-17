from django.db.models.signals import post_save
from django.dispatch import receiver
from accounts.models import User


@receiver(post_save, sender=User)
def user_post_save(sender, instance, created, **kwargs):
    """Signal handlers for user model."""
    if created:
        # Additional user initialization can be added here
        pass

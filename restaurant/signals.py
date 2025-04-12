from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from .models import Review,Restaurant

@receiver([post_save,post_delete],sender=Review)
def update_restaurant_rating(sender,instance,**kwargs):
    """Signal to update restaurant's rating when a review is saved or deleted."""
    restaurant=instance.restaurant
    restaurant.update_rating()
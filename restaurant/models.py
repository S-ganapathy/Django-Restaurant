from django.db import models
from django.db.models import Avg
from multiselectfield import MultiSelectField
from django.contrib.auth.models import User
from datetime import time
from django.utils import timezone
# Create your models here.

FOOD_TYPES=[
    ('veg','Vegetarian'),
    ('non_veg','Non-Vegetarian'),
    ('vegan','Vegan')
    ]

CUISINE_CHOICES =[
    ('Indian', 'Indian'),
    ('Chinese', 'Chinese'),
    ('Italian', 'Italian'),
    ('Mexican', 'Mexican'),
    ('Mediterranean', 'Mediterranean'),
    ('Thai', 'Thai'),
    ('French', 'French'),
    ('Spanish', 'Spanish'),
    ('Turkish', 'Turkish'),
    ('American', 'American'),
    ]

class Restaurant(models.Model):
    """Represents a restaurant entity with all relevant attributes."""


    title=models.CharField(max_length=255)
    owner=models.ForeignKey(User,on_delete=models.CASCADE)
    location=models.CharField(max_length=255)
    address=models.TextField(blank=True,null=True)
    cost_of_two=models.DecimalField(max_digits=6, decimal_places=2,blank=True,null=True)
    open_time=models.TimeField(default=time(9,0))
    close_time=models.TimeField(default=time(22,0))
    rating=models.DecimalField(max_digits=2,decimal_places=1,blank=True,null=True,default=0)

    food_type=MultiSelectField(choices=FOOD_TYPES,default='veg')
    cuisines=MultiSelectField(choices=CUISINE_CHOICES,blank=True,null=True)
    is_spotlight=models.BooleanField(default=False)

    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.title} - {self.location}'
    
    def is_open(self):
        current_time=timezone.now().time()

        if self.close_time < self.open_time:
            return self.open_time <= current_time or current_time <= self.close_time

        else:
            return self.open_time <= current_time <= self.close_time
    
    def update_rating(self):
        new_rating=self.reviews.aggregate(average_rating=Avg('rating'))['average_rating']
        self.rating=new_rating
        self.save()

    
class Dish(models.Model):
    """Represents individual dishes for a restaurant's menu."""

    restaurant=models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='dishes')
    name=models.CharField(max_length=255)
    description=models.TextField(null=True, blank=True)
    price=models.DecimalField(max_digits=6,decimal_places=2)
    food_type=models.CharField(max_length=255,choices=FOOD_TYPES,default='veg')
    cuisine=models.CharField(max_length=255,choices=CUISINE_CHOICES,blank=True,null=True)
    updated_at=models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.name} - {self.food_type}'



class Review(models.Model):
    """Represents reviews and ratings given by users."""

    restaurant=models.ForeignKey(Restaurant,on_delete=models.CASCADE, related_name='reviews')
    user=models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    rating=models.DecimalField(max_digits=2,decimal_places=1)
    comment=models.TextField(null=True,blank=True)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)

    class Meta:
        constraints=[
            models.UniqueConstraint(fields=['user','restaurant'],name='unique_review')
        ]
        ordering=['-created_at']
    
    def __str__(self):
        return f'Review by {self.user.username} for {self.restaurant.title}'


class BookmarkedRestaurant(models.Model):
    """Allows users to bookmark restaurants."""
    user=models.ForeignKey(User,on_delete=models.CASCADE,related_name='bookmarkes')
    restaurant=models.ForeignKey(Restaurant, on_delete=models.CASCADE,related_name='bookmarkes')
    created_at=models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints=[
            models.UniqueConstraint(fields=['user','restaurant'],name='unique_bookmark')
        ]
    
    def __str__(self):
        return f'{self.user.username} bookmarked {self.restaurant.title}'


class VisitedRestaurant(models.Model):
    """Tracks which restaurants a user has marked as visited."""
    user=models.ForeignKey(User, on_delete=models.CASCADE,related_name='visited')
    restaurant=models.ForeignKey(Restaurant, on_delete=models.CASCADE,related_name='visited')
    created_at=models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints=[
            models.UniqueConstraint(fields=['user','restaurant'],name='unique_visited')
        ]
    
    def __str__(self):
        return f"{self.user.username} visited {self.restaurant.title}"


class RestaurantImage(models.Model):
    restaurant=models.ForeignKey(Restaurant,on_delete=models.CASCADE,related_name='images')
    image=models.ImageField(upload_to='restaurant_images/')

    def __str__(self):
        return f'Image for {self.restaurant.title}'
from django.contrib import admin
from .models import Restaurant,Dish,Review,RestaurantImage
from django.contrib.admin import SimpleListFilter
# Register your models here.

class DishInline(admin.TabularInline):
    model=Dish
    fields=[('name','food_type'),('price','cuisine')]
    extra=1

class ReviewInline(admin.StackedInline):
    model=Review
    fields=[('user','rating'),'comment']
    extra=0

class RestaurantImageInline(admin.TabularInline):
    model=RestaurantImage
    extra=1



# Custom filter for food_type
class FoodTypeFilter(SimpleListFilter):
    title = 'Food Type'
    parameter_name = 'food_type'

    def lookups(self, request, model_admin):
        return [
            ('veg', 'Vegetarian'),
            ('non_veg', 'Non-Vegetarian'),
            ('vegan', 'Vegan')
        ]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(food_type__contains=self.value())  # Filtering multi-select
        return queryset

# Custom filter for cuisines
class CuisineFilter(SimpleListFilter):
    title = 'Cuisine'
    parameter_name = 'cuisines'

    def lookups(self, request, model_admin):
        return [
            ('Indian', 'Indian'),
            ('Chinese', 'Chinese'),
            ('Italian', 'Italian'),
            ('Mexican', 'Mexican'),
            ('Mediterranean', 'Mediterranean'),
            ('Thai', 'Thai'),
            ('French', 'French'),
            ('Spanish', 'Spanish'),
            ('Turkish', 'Turkish'),
            ('American', 'American')
        ]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(cuisines__contains=self.value())  # Filtering multi-select
        return queryset


@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):
    list_display = ['title', 'location', 'cost_of_two', 'rating', 'is_spotlight']
    list_filter = ['is_spotlight', FoodTypeFilter, CuisineFilter]  # Use custom filters
    search_fields = ['title', 'location']
    list_editable = ['cost_of_two']
    fields = [
        ('title', 'location'), 'address', 
        ('open_time', 'close_time'), 
        ('rating', 'cost_of_two'), 
        ('food_type', 'cuisines'), 
        ('is_spotlight', 'owner')
    ]
    inlines = [RestaurantImageInline, ReviewInline, DishInline]



@admin.register(Dish)
class DishAdmin(admin.ModelAdmin):
    list_display=['restaurant','name','food_type','price','cuisine']
    list_filter=['food_type','cuisine']
    search_fields=['name','restaurant']

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display=['restaurant','user','comment','rating']



import django_filters 
from django.db.models import Q,F
from .models import Restaurant
from django.utils import timezone


class RestaurantFilter(django_filters.FilterSet):
    city=django_filters.CharFilter(field_name='location',lookup_expr='icontains')
    food_type=django_filters.CharFilter(method='filter_food_type')
    cuisines=django_filters.CharFilter(method='filter_cuisines')
    rating=django_filters.NumberFilter(field_name='rating',lookup_expr='gte')
    cost_of_two=django_filters.NumberFilter(field_name='cost_of_two',lookup_expr='gte')
    is_open=django_filters.CharFilter(method='filter_is_open')
    search = django_filters.CharFilter(method='filter_search')

    sort_by=django_filters.OrderingFilter(
        fields=(
            ('rating','rating'),
            ('cost_of_two','cost_of_two'),
        )
    )

    class Meta:
        model=Restaurant
        fields=['city','rating','cost_of_two']
    
    def filter_food_type(self, queryset, name, value):

        if self.request: 
            food_types=self.request.GET.getlist('food_type')
            query=Q()
            for food_type in food_types:
                query |= Q(food_type__iregex=rf"(^|,){food_type}(,|$)")
        
        return queryset.filter(query)
    
    def filter_cuisines(self, queryset, name, value):
        if self.request:
            cuisines=self.request.GET.getlist('cuisines')
            query=Q()
            for cuisine in cuisines:
                query |= Q(cuisines__icontains=cuisine)
        return queryset.filter(query)
    
    def filter_is_open(self, queryset, name, value):
        if value == 'on':
            current_time=timezone.now().time()
            queryset=queryset.filter(
                Q(open_time__lte=current_time, close_time__gte=current_time) |
                Q(open_time__gte=F('close_time')),
                Q(open_time__lte=current_time) | Q(close_time__gte=current_time)
            )
        return queryset
    
    def filter_search(self, queryset, name, value):
        return queryset.filter(
            Q(title__icontains=value) | 
            Q(cuisines__icontains=value) |
            Q(location__icontains=value)
        )

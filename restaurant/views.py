from django.views.generic import ListView,DetailView,UpdateView,DeleteView,TemplateView
from django.views import View
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse,reverse_lazy
from .models import Restaurant, BookmarkedRestaurant, VisitedRestaurant, Review
from django.contrib.auth.models import User
from .forms import RestaurantFilterForm,ReviewForm,UserRegistrationForm
from django.db.models.functions import Upper
from django.db.models import Q
from django.http import JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseForbidden
from .filters import RestaurantFilter
from django.contrib.auth import login
from django.views.generic.edit import FormView
from django.core.exceptions import PermissionDenied
# Create your views here.

class RestaurantListView(ListView):
    model=Restaurant
    template_name='restaurant/restaurant_list.html'
    context_object_name='restaurants'
    filterset_class=RestaurantFilter
    paginate_by=5

    def get_queryset(self):
        queryset=Restaurant.objects.all()
        self.filterset=self.filterset_class(self.request.GET,queryset=queryset, request=self.request)
        return self.filterset.qs

    def get_context_data(self, **kwargs):
        context=super().get_context_data(**kwargs)
        context['cities'] = Restaurant.objects.annotate(upper_location=Upper('location')).values_list('upper_location', flat=True).distinct()
        context['form']=RestaurantFilterForm(self.request.GET)
        return context
    

class RestaurantDetailView(DetailView):
     model=Restaurant
     template_name='restaurant/restaurant_detail.html'
     context_object_name='restaurant'

     def get_context_data(self, **kwargs):
          context=super().get_context_data(**kwargs)
          context['veg_dishes']=self.object.dishes.filter(food_type='veg')
          context['non_veg_dishes']=self.object.dishes.filter(food_type='non_veg')
          context['vegan_dishes']=self.object.dishes.filter(food_type='vegan')
          if self.request.user.is_authenticated:
            context['is_bookmarked'] = self.object.bookmarkes.filter(user=self.request.user).exists()
            context['is_visited'] = self.object.visited.filter(user=self.request.user).exists()
            context['is_rated']=self.object.reviews.filter(user=self.request.user).exists()
          return context
     
     def post(self, request, *args, **kwargs):
          if self.request.user.is_authenticated:
            restaurant=self.get_object()
            form=ReviewForm(request.POST)
            if form.is_valid():
                review=form.save(commit=False)
                review.restaurant=restaurant
                review.user=request.user
                review.save()
                return redirect(reverse('restaurant_detail',kwargs={'pk':restaurant.id}))
          else:
              return HttpResponseForbidden("You must be logged-in to post a review.")
                
class ToggleBookmarkView(LoginRequiredMixin,View):
    def post(self, request, *args, **kwargs):
        restaurant_id = kwargs.get('restaurant_id')
        restaurant = get_object_or_404(Restaurant, id=restaurant_id)
        bookmark, created = BookmarkedRestaurant.objects.get_or_create(
            user=request.user,
            restaurant=restaurant
        )

        if not created:
            bookmark.delete()
            is_bookmarked = False
        else:
            is_bookmarked = True

        return JsonResponse({'is_bookmarked': is_bookmarked})
    

class ToggleVisitedView(LoginRequiredMixin,View):
    def post(self, request, *args, **kwargs):
        restaurant_id = kwargs.get('restaurant_id')
        restaurant = get_object_or_404(Restaurant, id=restaurant_id)
        visited, created = VisitedRestaurant.objects.get_or_create(
            user=request.user,
            restaurant=restaurant
        )

        if not created:
            visited.delete()
            is_visited = False
        else:
            is_visited = True

        return JsonResponse({'is_visited': is_visited})

class UserRegistrationView(FormView):
    template_name='accounts/user_registration.html'
    form_class=UserRegistrationForm
    success_url=reverse_lazy('restaurant_list')

    def form_valid(self, form):
        user=form.save()
        login(self.request, user)
        return super().form_valid(form)

class UserProfileUpdateView(LoginRequiredMixin,UpdateView):
    model=User
    fields=('first_name','last_name','email',)
    template_name='accounts/user_profile.html'
    success_url=reverse_lazy('user_profile')

    def get_object(self):
        return self.request.user

class ReviewDeleteView(LoginRequiredMixin,DeleteView):

    model=Review

    def get_success_url(self):
        return reverse_lazy('restaurant_detail',kwargs={'pk':self.object.restaurant.pk})

    def get_object(self, queryset = None):
        review=super().get_object(queryset)
        if review.user != self.request.user:
            raise PermissionDenied
        return review

    def get(self,request, *args,**kwargs):
        self.object=self.get_object()
        self.object.delete()
        return redirect(self.get_success_url())
    
class ReviewEditView(LoginRequiredMixin, UpdateView):
    model=Review
    form_class=ReviewForm
    template_name='restaurant/edit_review.html'

    def get_success_url(self):
        return reverse_lazy('restaurant_detail',kwargs={'pk':self.object.restaurant.pk})
    
    def get_queryset(self):
        return Review.objects.filter(user=self.request.user)
    
class BookmarkedRestaurantsView(LoginRequiredMixin,ListView):
    model=Restaurant
    template_name='restaurant/list_restaurants.html'
    context_object_name='restaurants'

    def get_queryset(self):
        book_marked=BookmarkedRestaurant.objects.filter(user=self.request.user).select_related('restaurant').values_list('restaurant',flat=True)
        return Restaurant.objects.filter(id__in=book_marked)
    
    def get_context_data(self, **kwargs):
        context=super().get_context_data(**kwargs)
        context['bookmarked']=True
        return context
    
class VisitedRestaurantsView(LoginRequiredMixin,ListView):
    model=Restaurant
    template_name='restaurant/list_restaurants.html'
    context_object_name='restaurants'

    def get_queryset(self):
        visited=VisitedRestaurant.objects.filter(user=self.request.user).select_related('restaurant').values_list('restaurant',flat=True)
        return Restaurant.objects.filter(id__in=visited)
    
    def get_context_data(self, **kwargs):
        context=super().get_context_data(**kwargs)
        context['visited']=True
        return context
    
class SpotlightRestaurantView(ListView):
    model=Restaurant
    template_name='restaurant/list_restaurants.html'
    context_object_name='restaurants'

    def get_queryset(self):
        return Restaurant.objects.filter(is_spotlight=True)
    
    def get_context_data(self, **kwargs):
        context=super().get_context_data(**kwargs)
        context['spotlight']=True
        return context
    
class HomeView(TemplateView):
    template_name='restaurant/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['restaurants'] = Restaurant.objects.order_by('-rating')[:4]
        return context

from django.urls import path
from  restaurant import views
from django.contrib.auth import views as auth_views


urlpatterns=[
    path('restaurants/',views.RestaurantListView.as_view(),name='restaurant_list'),
    path('<int:pk>/',views.RestaurantDetailView.as_view(),name='restaurant_detail'),
    path('bookmark/<int:restaurant_id>/',views.ToggleBookmarkView.as_view(),name='toggle_bookmark'),
    path('visited/<int:restaurant_id>/',views.ToggleVisitedView.as_view(),name='toggle_visited'),
    path('register/',views.UserRegistrationView.as_view(),name='user_registration'),
    path('login/',auth_views.LoginView.as_view(template_name='accounts/user_login.html'),name='user_login'),
    path('logout/',auth_views.LogoutView.as_view(),name='user_logout'),

    path('password_reset/',
         auth_views.PasswordResetView.as_view(template_name='accounts/password_reset.html',email_template_name='accounts/password_reset_email.html'),
         name='password_reset'
         ),
    path('password_reset/done/',
         auth_views.PasswordResetDoneView.as_view(template_name='accounts/password_reset_done.html'),
         name='password_reset_done'
         ),
    path('password_reset/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(template_name='accounts/password_reset_confirm.html'),
         name='password_reset_confirm'
         ),
    path('password_reset/complete/',
         auth_views.PasswordResetCompleteView.as_view(template_name='accounts/password_reset_complete.html'),
         name='password_reset_complete'
         ),

    path('password_change/',auth_views.PasswordChangeView.as_view(template_name='accounts/password_change.html'),
         name='password_change'
         ),
    path('password_change_done/',auth_views.PasswordChangeDoneView.as_view(template_name='accounts/password_change_done.html'),
         name='password_change_done'
         ),
     path('profile/',views.UserProfileUpdateView.as_view(),name='user_profile'),
     path('review/delete/<int:pk>/',views.ReviewDeleteView.as_view(),name='review_delete'),
     path('review/edit/<int:pk>/',views.ReviewEditView.as_view(),name='review_edit'),
     path('bookmarked/restaurants/',views.BookmarkedRestaurantsView.as_view(),name='bookmarked_restaurants'),
     path('visited/restaurants/',views.VisitedRestaurantsView.as_view(),name='visited_restaurants'),
     path('spotlight/restaurants/',views.SpotlightRestaurantView.as_view(),name='spotlight_restaurants'),
     path('',views.HomeView.as_view(),name='home')
]
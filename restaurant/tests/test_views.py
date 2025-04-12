from django.test import TestCase
from django.urls import reverse,resolve
from ..models import Restaurant,Dish,Review,BookmarkedRestaurant,VisitedRestaurant
from ..views import RestaurantListView,RestaurantDetailView,ReviewDeleteView,ReviewEditView
from ..views import BookmarkedRestaurantsView,VisitedRestaurantsView,SpotlightRestaurantView,HomeView
from ..forms import RestaurantFilterForm,ReviewForm
from django.contrib.auth.models import User
from unittest.mock import patch
from datetime import time,datetime
from django.core.exceptions import PermissionDenied

class RestaurantListViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.testuser=User.objects.create_user(username='testuser1',email='testuser1@gmail.com',password='user1@123')
        Restaurant.objects.create(
            title='Restaurant A',owner=cls.testuser,location='City A', food_type='veg', rating=4.5, cost_of_two=500, open_time=time(9,0), close_time=time(22,0)
        )
        Restaurant.objects.create(
            title='Restaurant B',owner=cls.testuser, location='City B', food_type='non_veg', rating=3.8, cost_of_two=700, open_time=time(10,0), close_time=time(22,0)
        )
        Restaurant.objects.create(
            title='Restaurant C',owner=cls.testuser, location='City A', food_type='veg', rating=4.9, cost_of_two=1000, open_time=time(11,0), close_time=time(23,0)
        )

    def test_restaurant_list_url_resolves_restaurant_list_view(self):
        view=resolve('/restaurants/')
        self.assertEqual(view.func.view_class,RestaurantListView)
    
    def test_view_uses_correct_template(self):
        response=self.client.get(reverse('restaurant_list'))
        self.assertTemplateUsed(response,'restaurant/restaurant_list.html')

    def test_restaurant_list_view_context(self):
        response = self.client.get(reverse('restaurant_list')) 
        self.assertEqual(response.status_code, 200)
        self.assertIn('form', response.context)
        self.assertIsInstance(response.context['form'], RestaurantFilterForm)
        self.assertIn('cities', response.context)
        cities = response.context['cities']
        self.assertEqual(list(cities), ['CITY A', 'CITY B'])  
        self.assertIn('restaurants', response.context)
        self.assertEqual(len(response.context['restaurants']), 3)

    def test_filter_form_valid(self):
        response=self.client.get(reverse('restaurant_list'),{
            'city': 'City A',
            'food_type': 'veg',
            'rating': 4,
            'cost_of_two': 500
        })
        self.assertEqual(response.status_code,200)
        self.assertEqual(len(response.context['restaurants']),2)

    def test_filter_by_city(self):
        response = self.client.get(reverse('restaurant_list'), {'city': 'City A'})
        self.assertEqual(len(response.context['restaurants']), 2) 
    
    def test_filter_by_food_type(self):
        response = self.client.get(reverse('restaurant_list'), {'food_type': 'non_veg'})
        self.assertEqual(len(response.context['restaurants']), 1)
        response = self.client.get(reverse('restaurant_list'), {'food_type': 'veg'})
        self.assertEqual(len(response.context['restaurants']), 2)

    def test_sort_by_rating(self):
        response = self.client.get(reverse('restaurant_list'), {'sort_by': '-rating'})
        restaurants = response.context['restaurants']
        self.assertEqual(float(restaurants[0].rating), 4.9) 
        self.assertEqual(float(restaurants[1].rating),4.5)
    
    def test_sort_by_cost(self):
        response = self.client.get(reverse('restaurant_list'), {'sort_by': 'cost_of_two'})
        restaurants = response.context['restaurants']
        self.assertEqual(restaurants[0].cost_of_two, 500)
        self.assertEqual(restaurants[1].cost_of_two,700)

    def test_filter_by_is_open(self):
        with patch('django.utils.timezone.now',return_value=datetime(2024,1,1,22,30)):
            response = self.client.get(reverse('restaurant_list'), {'is_open':'on'})
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(response.context['restaurants']), 1)

class RestaurantSearchTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.testuser=User.objects.create_user(username='testuser1',email='testuser1@gmail.com',password='user1@123')
        cls.restaurant1 = Restaurant.objects.create(
            owner=cls.testuser,
            title="Pizza Place", 
            location="New York", 
            food_type='non_veg',
            cuisines=["Italian"], 
        )
        cls.restaurant2 = Restaurant.objects.create(
            owner=cls.testuser,
            title="Sushi World", 
            location="San Francisco",
            food_type='non_veg', 
            cuisines=["Japanese"], 
        )
        cls.restaurant3 = Restaurant.objects.create(
            owner=cls.testuser,
            title="Veggie Delight", 
            food_type='veg',
            location="New York", 
            cuisines=["American"], 
        )

    def test_search_by_title(self):
        response = self.client.get(reverse('restaurant_list'), {'search': 'Pizza'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Pizza Place")
        self.assertNotContains(response, "Sushi World")

    def test_search_by_cuisine(self):
        response = self.client.get(reverse('restaurant_list'), {'search': 'Japanese'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Sushi World")
        self.assertNotContains(response, "Veggie Delight")

    def test_search_by_location(self):
        response = self.client.get(reverse('restaurant_list'), {'search': 'New York'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Pizza Place")
        self.assertContains(response, "Veggie Delight")
        self.assertNotContains(response, "Sushi World")

    def test_search_case_insensitivity(self):
        response = self.client.get(reverse('restaurant_list'), {'search': 'sushi'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Sushi World")

    def test_empty_search_query(self):
        response = self.client.get(reverse('restaurant_list'), {'search': ''})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Pizza Place")
        self.assertContains(response, "Sushi World")
        self.assertContains(response, "Veggie Delight")

    def test_search_no_results(self):
        response = self.client.get(reverse('restaurant_list'), {'search': 'Steak'})
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "Pizza Place")
        self.assertNotContains(response, "Sushi World")
        self.assertNotContains(response, "Veggie Delight")
        self.assertContains(response, "No Restaurant Found")

    def test_search_with_filters(self):
        response = self.client.get(reverse('restaurant_list'), {
            'search': 'New York', 
            'food_type': 'veg'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Veggie Delight")
        self.assertNotContains(response, "Pizza Place")


class DetailViewTestDataSetUp(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.testuser1=User.objects.create_user(username='testuser1',email='testuser1@gmail.com',password='user1@123')
        cls.testuser2=User.objects.create_user(username='testuser2',email='testuser2@gmail.com',password='user2@123')

        cls.testrestaurant=Restaurant.objects.create(
            title='testrestaurant',owner=cls.testuser1,location='City A', food_type=['veg','non_veg','vegan'], rating=4.5, cost_of_two=500, open_time='10:00', close_time='20:00'
        )

        cls.veg_dish=Dish.objects.create(
            restaurant=cls.testrestaurant,name='veg Dish',food_type='veg',price=150
        )

        cls.non_veg_dish=Dish.objects.create(
            restaurant=cls.testrestaurant,name='non veg Dish',food_type='non_veg',price=180
        )

        cls.vegan_dish=Dish.objects.create(
            restaurant=cls.testrestaurant,name='vegan Dish',food_type='vegan',price=120
        )

class RestaurantDetailViewTests(DetailViewTestDataSetUp):
    def test_restaurant_detail_url_resolves_restaurant_detail_view(self):
        view=resolve(f'/{self.testrestaurant.id}/')
        self.assertEqual(view.func.view_class,RestaurantDetailView)
    
    def test_view_uses_correct_template(self):
        response=self.client.get(reverse('restaurant_detail',kwargs={'pk':self.testrestaurant.id}))
        self.assertTemplateUsed(response,'restaurant/restaurant_detail.html') 

    def test_anonymous_user_detail_view_context_data(self):
        response=self.client.get(reverse('restaurant_detail',kwargs={'pk':self.testrestaurant.id}))
        self.assertEqual(response.status_code,200)
        self.assertEqual(response.context['restaurant'],self.testrestaurant)
        self.assertIn(self.veg_dish, response.context['veg_dishes'])
        self.assertIn(self.non_veg_dish, response.context['non_veg_dishes'])
        self.assertIn(self.vegan_dish, response.context['vegan_dishes'])
        self.assertNotIn('is_bookmarked', response.context)
        self.assertNotIn('is_visited', response.context)
        self.assertNotIn('is_rated', response.context)

    def test_loged_in_user_detail_view_context_data(self):
        self.client.login(username='testuser2',password='user2@123')
        response=self.client.get(reverse('restaurant_detail',kwargs={'pk':self.testrestaurant.id}))
        self.assertEqual(response.status_code,200)
        self.assertEqual(response.context['restaurant'],self.testrestaurant)
        self.assertIn(self.veg_dish, response.context['veg_dishes'])
        self.assertIn(self.non_veg_dish, response.context['non_veg_dishes'])
        self.assertIn(self.vegan_dish, response.context['vegan_dishes'])
        self.assertIn('is_bookmarked', response.context)
        self.assertIn('is_visited', response.context)
        self.assertIn('is_rated', response.context)

    def test_anonymous_user_template_rendering(self):
        response=self.client.get(reverse('restaurant_detail',kwargs={'pk':self.testrestaurant.id}))
        self.assertEqual(response.status_code,200)
        self.assertContains(response, 'testrestaurant')
        self.assertContains(response, 'vegitarian') 
        self.assertContains(response, 'Non vegitarian')
        self.assertContains(response, 'vegan')
        self.assertNotContains(response, 'Bookmark')
        self.assertNotContains(response, 'Visited')
        self.assertNotContains(response,'Rate us')

    def test_login_user_template_rendering(self):
        self.client.login(username='testuser2',password='user2@123')
        response=self.client.get(reverse('restaurant_detail',kwargs={'pk':self.testrestaurant.id}))
        self.assertEqual(response.status_code,200)
        self.assertContains(response, 'testrestaurant')
        self.assertContains(response, 'vegitarian') 
        self.assertContains(response, 'Non vegitarian')
        self.assertContains(response, 'vegan')
        self.assertContains(response, 'Bookmark')
        self.assertContains(response, 'Visited')
        self.assertContains(response,'Rate us')
    
    def test_rate_us_not_rendered_if_already_rated(self):
        self.client.login(username='testuser2',password='user2@123')
        Review.objects.create(restaurant=self.testrestaurant,user=self.testuser2,rating=3.5,comment="this is test rating comment")
        response=self.client.get(reverse('restaurant_detail',kwargs={'pk':self.testrestaurant.id}))
        self.assertNotContains(response,'Rate us')
        self.assertEqual(response.context['restaurant'].reviews.first(),Review.objects.first())

    def test_anonymous_user_review_submission(self):
        response = self.client.post(
            reverse('restaurant_detail', kwargs={'pk': self.testrestaurant.id}),
            data={'rating': 4, 'comment': 'Great food!'}
        )
        self.assertEqual(response.status_code,403)

    def test_review_submission(self):
        self.client.login(username='testuser2',password='user2@123')
        response = self.client.post(
            reverse('restaurant_detail', kwargs={'pk': self.testrestaurant.id}),
            data={'rating': 4, 'comment': 'Great food!'}
        )

        self.assertEqual(response.status_code,302)
        self.assertTrue(Review.objects.filter(restaurant=self.testrestaurant,user=self.testuser2).exists())
        review=Review.objects.get(restaurant=self.testrestaurant,user=self.testuser2)
        self.assertEqual(review.rating,4)
        self.assertEqual(review.comment,'Great food!')

class ToggleBookmarkViewTests(DetailViewTestDataSetUp):
    def test_anonymous_toogle_bookmark_redirects(self):
        response = self.client.post(reverse('toggle_bookmark', kwargs={'restaurant_id': self.testrestaurant.id}))
        self.assertEqual(response.status_code,302)

    def test_toggle_bookmark(self):
        self.client.login(username='testuser2',password='user2@123')
        response = self.client.post(reverse('toggle_bookmark', kwargs={'restaurant_id': self.testrestaurant.id}))
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {'is_bookmarked': True})

        response = self.client.post(reverse('toggle_bookmark', kwargs={'restaurant_id': self.testrestaurant.id}))
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {'is_bookmarked': False})

class ToggleVisistedViewTests(DetailViewTestDataSetUp):
    def test_anonymous_toogle_visited_redirects(self):
        response = self.client.post(reverse('toggle_bookmark', kwargs={'restaurant_id': self.testrestaurant.id}))
        self.assertEqual(response.status_code,302)

    def test_toggle_visited(self):
        self.client.login(username='testuser2',password='user2@123')
        response = self.client.post(reverse('toggle_visited', kwargs={'restaurant_id': self.testrestaurant.id}))
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {'is_visited': True})

        response = self.client.post(reverse('toggle_visited', kwargs={'restaurant_id': self.testrestaurant.id}))
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {'is_visited': False})

class DeleteReviewViewTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.testuser1=User.objects.create_user(username='testuser1',email='testuser1@gmail.com',password='user1@123')
        cls.testuser2=User.objects.create_user(username='testuser2',email='testuser2@gmail.com',password='user2@123')
        cls.testuser3=User.objects.create_user(username='testuser3',email='testuser3@gmail.com',password='user3@123')

        cls.testrestaurant=Restaurant.objects.create(
            title='testrestaurant',owner=cls.testuser1,location='City A', food_type=['veg','non_veg','vegan'], rating=4.5, cost_of_two=500, open_time='10:00', close_time='20:00'
        )
        cls.testreview=Review.objects.create(
            restaurant=cls.testrestaurant, user=cls.testuser2, rating=4, comment="nice hotel to have all varities of food"
        )        

    def test_delete_review_url_resolves_delete_review_view(self):
        view=resolve(f'/review/delete/{self.testreview.id}/')
        self.assertEqual(view.func.view_class,ReviewDeleteView)

    def test_anonymous_user_redirect_to_login(self):
        response=self.client.get(reverse('review_delete',kwargs={'pk':self.testreview.pk}))
        self.assertRedirects(response,f"{reverse('user_login')}?next={reverse('review_delete',kwargs={'pk':self.testreview.pk})}")
        self.testreview.refresh_from_db()
        self.assertTrue(self.testrestaurant.reviews.filter(user=self.testuser2).exists())
    
    def test_user_cannot_delete_other_user_reviews(self):
        self.client.login(username='testuser3',password='user3@123')
        response=self.client.get(reverse('review_delete',kwargs={'pk':self.testreview.pk}))
        self.assertEqual(response.status_code,403)
        self.testreview.refresh_from_db()
        self.assertTrue(self.testrestaurant.reviews.filter(user=self.testuser2).exists())
    
    def test_valid_user_successful_deltion(self):
        self.client.login(username='testuser2',password='user2@123')
        response=self.client.get(reverse('review_delete',kwargs={'pk':self.testreview.pk}))
        self.assertRedirects(response,reverse('restaurant_detail',kwargs={'pk':self.testrestaurant.id}))
        self.assertFalse(Review.objects.filter(user=self.testuser2).exists())

class EditReviewViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.testuser1=User.objects.create_user(username='testuser1',email='testuser1@gmail.com',password='user1@123')
        cls.testuser2=User.objects.create_user(username='testuser2',email='testuser2@gmail.com',password='user2@123')

        cls.testrestaurant=Restaurant.objects.create(
            title='testrestaurant',owner=cls.testuser1,location='City A', food_type=['veg','non_veg','vegan'], rating=4.5, cost_of_two=500, open_time='10:00', close_time='20:00'
        )
        cls.testreview=Review.objects.create(
            restaurant=cls.testrestaurant, user=cls.testuser2, rating=4, comment="nice hotel to have all varities of food"
        )

    def test_edit_review_url_resolves_edit_review_view(self):
        view=resolve(f'/review/edit/{self.testreview.id}/')
        self.assertEqual(view.func.view_class,ReviewEditView)
    
    def test_edit_review_view_uses_correct_template(self):
        self.client.login(username='testuser2',password='user2@123')
        response=self.client.get(reverse('review_edit',kwargs={'pk':self.testreview.id}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response,'restaurant/edit_review.html')
    
    def test_edit_review_page_contains_correct_contents(self):
        self.client.login(username='testuser2',password='user2@123')
        response=self.client.get(reverse('review_edit',kwargs={'pk':self.testreview.id}))
        self.assertEqual(response.status_code, 200)
        form=response.context['form']
        self.assertEqual(form.initial['comment'],"nice hotel to have all varities of food")
        self.assertEqual(form.initial['rating'],4)
    
    def test_edit_review_view_update_content(self):
        self.client.login(username='testuser2',password='user2@123')
        response=self.client.post(reverse('review_edit',kwargs={'pk':self.testreview.id}),{
            'rating':3,
            'comment':"this is the testing comment for testcase"
        })
        self.assertRedirects(response,reverse('restaurant_detail',kwargs={'pk':self.testreview.restaurant.id}))
        self.testreview.refresh_from_db()
        review=Review.objects.get(user=self.testuser2)
        self.assertEqual(review.rating,self.testreview.rating)
        self.assertEqual(review.comment,self.testreview.comment)
        

class BookmarkedRestaurantsViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.testuser1=User.objects.create_user(username='testuser1',email='testuser1@gmail.com',password='user1@123')
        cls.testuser2=User.objects.create_user(username='testuser2',email='testuser2@gmail.com',password='user2@123')
        cls.testuser3=User.objects.create_user(username='testuser3',email='testuser3@gmail.com',password='user3@123')
        cls.testuser4=User.objects.create_user(username='testuser4',email='testuser4@gmail.com',password='user4@123')

        cls.restaurant1=Restaurant.objects.create(
            title='Restaurant A',owner=cls.testuser1,location='City A', food_type=['veg','non_veg','vegan'], rating=4.5, cost_of_two=500, open_time='10:00', close_time='20:00'
        )
        cls.restaurant2=Restaurant.objects.create(
            title='Restaurant B',owner=cls.testuser2, location='City B', food_type='non_veg', rating=3.8, cost_of_two=700, open_time='11:00', close_time='20:00'
        )
        cls.restaurant3=Restaurant.objects.create(
            title='Restaurant C',owner=cls.testuser3, location='City A', food_type='veg', rating=4.9, cost_of_two=1000, open_time='09:00', close_time='23:00'
        )

        BookmarkedRestaurant.objects.create(user=cls.testuser4,restaurant=cls.restaurant1)
        BookmarkedRestaurant.objects.create(user=cls.testuser4,restaurant=cls.restaurant2)

    def setUp(self):
        self.client.login(username='testuser4',password='user4@123')
        self.response=self.client.get(reverse('bookmarked_restaurants'))

    def test_bookmarked_view_use_correct_template(self):
        self.assertEqual(self.response.status_code,200)
        self.assertTemplateUsed(self.response,'restaurant/list_restaurants.html')
    
    def test_bookmarked_url_resloves_bookmarked_view(self):
        view=resolve('/bookmarked/restaurants/')
        self.assertEqual(view.func.view_class, BookmarkedRestaurantsView)

    def test_anonymous_user_access_redirected(self):
        self.client.logout()
        response=self.client.get(reverse('bookmarked_restaurants'))
        self.assertRedirects(response,f"{reverse('user_login')}?next={reverse('bookmarked_restaurants')}")
    
    def test_view_retrun_only_bookmarked_restaurants_by_login_user(self):
        restaurants=self.response.context['restaurants']
        self.assertEqual(len(restaurants),2)
        self.assertEqual(restaurants[0].title,'Restaurant A')
        self.assertEqual(restaurants[1].title,'Restaurant B')
        self.assertContains(self.response,'Book Marked Restaurants')

class VisitedRestaurantsViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.testuser1=User.objects.create_user(username='testuser1',email='testuser1@gmail.com',password='user1@123')
        cls.testuser2=User.objects.create_user(username='testuser2',email='testuser2@gmail.com',password='user2@123')
        cls.testuser3=User.objects.create_user(username='testuser3',email='testuser3@gmail.com',password='user3@123')
        cls.testuser4=User.objects.create_user(username='testuser4',email='testuser4@gmail.com',password='user4@123')

        cls.restaurant1=Restaurant.objects.create(
            title='Restaurant A',owner=cls.testuser1,location='City A', food_type=['veg','non_veg','vegan'], rating=4.5, cost_of_two=500, open_time='10:00', close_time='20:00'
        )
        cls.restaurant2=Restaurant.objects.create(
            title='Restaurant B',owner=cls.testuser2, location='City B', food_type='non_veg', rating=3.8, cost_of_two=700, open_time='11:00', close_time='20:00'
        )
        cls.restaurant3=Restaurant.objects.create(
            title='Restaurant C',owner=cls.testuser3, location='City A', food_type='veg', rating=4.9, cost_of_two=1000, open_time='09:00', close_time='23:00'
        )

        VisitedRestaurant.objects.create(user=cls.testuser4,restaurant=cls.restaurant1)
        VisitedRestaurant.objects.create(user=cls.testuser4,restaurant=cls.restaurant2)

    def setUp(self):
        self.client.login(username='testuser4',password='user4@123')
        self.response=self.client.get(reverse('visited_restaurants'))

    def test_bookmarked_view_use_correct_template(self):
        self.assertEqual(self.response.status_code,200)
        self.assertTemplateUsed(self.response,'restaurant/list_restaurants.html')
    
    def test_bookmarked_url_resloves_bookmarked_view(self):
        view=resolve('/visited/restaurants/')
        self.assertEqual(view.func.view_class, VisitedRestaurantsView)

    def test_anonymous_user_access_redirected(self):
        self.client.logout()
        response=self.client.get(reverse('visited_restaurants'))
        self.assertRedirects(response,f"{reverse('user_login')}?next={reverse('visited_restaurants')}")
    
    def test_view_retrun_only_bookmarked_restaurants_by_login_user(self):
        restaurants=self.response.context['restaurants']
        self.assertEqual(len(restaurants),2)
        self.assertEqual(restaurants[0].title,'Restaurant A')
        self.assertEqual(restaurants[1].title,'Restaurant B')
        self.assertContains(self.response,'Visited Restaurants')


class SpotlightRestaurantsViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.testuser1=User.objects.create_user(username='testuser1',email='testuser1@gmail.com',password='user1@123')
        cls.testuser2=User.objects.create_user(username='testuser2',email='testuser2@gmail.com',password='user2@123')
        cls.testuser3=User.objects.create_user(username='testuser3',email='testuser3@gmail.com',password='user3@123')
        cls.testuser4=User.objects.create_user(username='testuser4',email='testuser4@gmail.com',password='user4@123')

        cls.restaurant1=Restaurant.objects.create(
            title='Restaurant A',owner=cls.testuser1,location='City A', food_type=['veg','non_veg','vegan'], rating=4.5, cost_of_two=500, open_time='10:00', close_time='20:00',is_spotlight=True
        )
        cls.restaurant2=Restaurant.objects.create(
            title='Restaurant B',owner=cls.testuser2, location='City B', food_type='non_veg', rating=3.8, cost_of_two=700, open_time='11:00', close_time='20:00'
        )
        cls.restaurant3=Restaurant.objects.create(
            title='Restaurant C',owner=cls.testuser3, location='City A', food_type='veg', rating=4.9, cost_of_two=1000, open_time='09:00', close_time='23:00',is_spotlight=True
        )

    def setUp(self):
        self.client.login(username='testuser4',password='user4@123')
        self.response=self.client.get(reverse('spotlight_restaurants'))

    def test_bookmarked_view_use_correct_template(self):
        self.assertEqual(self.response.status_code,200)
        self.assertTemplateUsed(self.response,'restaurant/list_restaurants.html')
    
    def test_bookmarked_url_resloves_bookmarked_view(self):
        view=resolve('/spotlight/restaurants/')
        self.assertEqual(view.func.view_class, SpotlightRestaurantView)

    def test_anonymous_user_status_200(self):
        self.client.logout()
        response=self.client.get(reverse('spotlight_restaurants'))
        self.assertEqual(response.status_code,200)
    
    def test_view_retrun_only_bookmarked_restaurants_by_login_user(self):
        restaurants=self.response.context['restaurants']
        self.assertEqual(len(restaurants),2)
        self.assertEqual(restaurants[0].title,'Restaurant A')
        self.assertEqual(restaurants[1].title,'Restaurant C')
        self.assertContains(self.response,'Spotlight Restaurants')
    
class HomeViewTests(TestCase):

    def test_homepage_use_correct_template(self):
        response=self.client.get(reverse('home'))
        self.assertEqual(response.status_code,200)
        self.assertTemplateUsed(response,'restaurant/home.html')
    
    def test_homepage_resolve_home_view(self):
        view=resolve('/')
        self.assertEqual(view.func.view_class,HomeView)

    def test_homepage_receives_restaurants_context(self):
        response=self.client.get(reverse('home'))
        self.assertIn('restaurants',response.context)


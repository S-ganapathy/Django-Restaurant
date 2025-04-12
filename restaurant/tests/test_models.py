from django.test import TestCase
from ..models import Restaurant, Dish, Review, BookmarkedRestaurant, VisitedRestaurant
from django.contrib.auth.models import User
from datetime import time,datetime
from unittest.mock import patch
from django.db.utils import IntegrityError


class RestaurantModelTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.testuser=User.objects.create_user(username='testuser1',email='testuser1@gmail.com',password='user1@123')
        cls.test_restaurant=Restaurant.objects.create(
            title='TestHotel',
            owner=cls.testuser,
            location='Mumbai',
            cost_of_two=400,
            address='hhh mmmm okokok',
            food_type=['veg','non_veg'],
            cuisines=['Indian','Chinese'],
            is_spotlight=True
        )

    def test_create_restaurant(self):
        self.assertEqual(self.test_restaurant.title,"TestHotel")
        self.assertEqual(self.test_restaurant.owner,self.testuser)
        self.assertEqual(self.test_restaurant.location,"Mumbai")
        self.assertEqual(self.test_restaurant.cost_of_two,400.00)            
        self.assertEqual(self.test_restaurant.food_type,['veg','non_veg'])
        self.assertEqual(self.test_restaurant.cuisines,['Indian','Chinese'])
        self.assertTrue(self.test_restaurant.is_spotlight)
        self.assertEqual(str(self.test_restaurant),f'{self.test_restaurant.title} - {self.test_restaurant.location}')
    
    def test_is_open_for_regular_hours(self):
        test_restaurant=Restaurant.objects.create(
            title='Test Restaurant',
            owner=self.testuser,
            location="Test City",
            open_time=time(9,0),
            close_time=time(22,0),
        )

        with patch('django.utils.timezone.now',return_value=datetime(2024,1,1,13,0)):
            self.assertTrue(test_restaurant.is_open())
        
        with patch('django.utils.timezone.now',return_value=datetime(2024,1,1,6,0)):
            self.assertFalse(test_restaurant.is_open())
        
    def test_is_open_past_midnight(self):
        test_restaurant=Restaurant.objects.create(
            title='Late night Hostel',
            owner=self.testuser,
            location="Test City",
            open_time=time(18,0),
            close_time=time(2,0),
        )

        with patch('django.utils.timezone.now',return_value=datetime(2024,1,1,1,0)):
            self.assertTrue(test_restaurant.is_open())
        
        with patch('django.utils.timezone.now',return_value=datetime(2024,1,1,17,0)):
            self.assertFalse(test_restaurant.is_open())

    def test_update_rating_with_reviews(self):
        testuser2=User.objects.create_user(username='testuser2',password='user2@123')
        testuser3=User.objects.create_user(username='testuser3',password='user3@123')

        Review.objects.create(restaurant=self.test_restaurant,user=self.testuser,rating=5)
        Review.objects.create(restaurant=self.test_restaurant,user=testuser2,rating=4)
        Review.objects.create(restaurant=self.test_restaurant,user=testuser3,rating=3)
        self.test_restaurant.refresh_from_db()
        self.assertEqual(self.test_restaurant.rating,4) # 5+4+3 = 12  |  12/3 = 4


class BaseTestDataSetUp(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.testuser=User.objects.create_user(username='testuser1',password='user1@123')
        cls.test_restaurant=Restaurant.objects.create(
            title='TestHotel',
            owner=cls.testuser,
            location='Mumbai',
        )


class DishModelTests(BaseTestDataSetUp):
    def setUp(self):
        self.test_dish=Dish.objects.create(
            restaurant=self.test_restaurant,
            name='Veg Fried Rice',
            description='Tasty fried rice',
            price=110,
            food_type='veg',
            cuisine='Chinese'
        )

    def test_create_dish(self):
        self.assertEqual(str(self.test_dish.restaurant),str(self.test_restaurant))
        self.assertEqual(self.test_dish.name,'Veg Fried Rice')
        self.assertEqual(self.test_dish.price,110.00)
        self.assertEqual(self.test_dish.description,'Tasty fried rice')

    def test_multiple_choice_fields(self):
        self.assertEqual(self.test_dish.food_type,'veg')
        self.assertEqual(self.test_dish.cuisine,'Chinese')

    def test_delete_restaurant_remove_accosiated_dish(self):
        test_dish2=Dish.objects.create(
            restaurant=self.test_restaurant,
            name='Chicken Fried Rice',
            description='Tasty Chickenfried rice',
            price=150,
        )

        self.assertEqual(Dish.objects.filter(restaurant=self.test_restaurant).count(),2)
        self.test_restaurant.delete()
        self.test_restaurant.save()
        self.assertEqual(Dish.objects.filter(restaurant=self.test_restaurant).count(),0)

    def test_str_method(self):
        self.assertEqual(str(self.test_dish),f'{self.test_dish.name} - {self.test_dish.food_type}')


class ReviewModelTests(BaseTestDataSetUp):
    def setUp(self):
        self.testuser2=User.objects.create_user(username='testuser2',password='user2@123')
        self.test_review=Review.objects.create(restaurant=self.test_restaurant,user=self.testuser2,rating=4.5,comment='Very nice restaurant test')
    
    def test_create_review(self):
        self.assertEqual(str(self.test_review.restaurant),f'{self.test_restaurant.title} - {self.test_restaurant.location}')
        self.assertEqual(str(self.test_review.user),self.testuser2.username)
        self.assertEqual(self.test_review.rating,4.5)
        self.assertEqual(self.test_review.comment,'Very nice restaurant test')
    
    def test_update_rating_on_new_review(self):
        self.testuser3=User.objects.create_user(username='testuser3',password='user3@123')
        Review.objects.create(restaurant=self.test_restaurant,user=self.testuser3,rating=2.5,comment='Ok')
        self.test_restaurant.refresh_from_db()
        self.assertEqual(self.test_restaurant.rating,3.5)
    
    def test_str_method(self):
        self.assertEqual(str(self.test_review),f'Review by {self.testuser2} for {self.test_restaurant.title}')

    def test_unique_constraint(self):
        with self.assertRaises(IntegrityError):
            Review.objects.create(restaurant=self.test_restaurant,user=self.testuser2,rating=3.5,comment='Moderate one')


class BookMarkedRestauarantTests(BaseTestDataSetUp):
    def setUp(self):
        self.testuser2=User.objects.create_user(username='testuser2',password='user2@123')
        self.test_bookmark=BookmarkedRestaurant.objects.create(user=self.testuser2,restaurant=self.test_restaurant)
    
    def test_create_bookmark(self):
        self.assertEqual(str(self.test_bookmark.restaurant),f'{self.test_restaurant.title} - {self.test_restaurant.location}')
        self.assertEqual(str(self.test_bookmark.user),self.testuser2.username)
    
    def test_str_method(self):
        self.assertEqual(str(self.test_bookmark),f'{self.testuser2.username} bookmarked {self.test_restaurant.title}')

    def test_unique_constraint(self):
        with self.assertRaises(IntegrityError):
            BookmarkedRestaurant.objects.create(user=self.testuser2,restaurant=self.test_restaurant)

class VisitedRestaurantTests(BaseTestDataSetUp):
    def setUp(self):
        self.testuser2=User.objects.create_user(username='testuser2',password='user2@123')
        self.test_visited=VisitedRestaurant.objects.create(user=self.testuser2,restaurant=self.test_restaurant)
    
    def test_create_visited(self):
        self.assertEqual(str(self.test_visited.restaurant),f'{self.test_restaurant.title} - {self.test_restaurant.location}')
        self.assertEqual(str(self.test_visited.user),self.testuser2.username)
    
    def test_str_method(self):
        self.assertEqual(str(self.test_visited),f'{self.testuser2.username} visited {self.test_restaurant.title}')

    def test_unique_constraint(self):
        with self.assertRaises(IntegrityError):
            VisitedRestaurant.objects.create(user=self.testuser2,restaurant=self.test_restaurant)

        








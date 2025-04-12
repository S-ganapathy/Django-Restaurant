from django.test import TestCase
from django.urls import reverse,resolve
from django.contrib.auth.models import User
from ..views import UserRegistrationView,UserProfileUpdateView
from django.contrib.auth import views as auth_views
from django.contrib.auth.forms import PasswordResetForm
from django.core import mail
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth.tokens import default_token_generator

class UserRegistrationViewTests(TestCase):
    def test_user_registration_url_resolves_user_registration_view(self):
        view=resolve('/register/')
        self.assertEqual(view.func.view_class,UserRegistrationView)

    def test_view_uses_correct_template(self):
        response=self.client.get(reverse('user_registration'))
        self.assertEqual(response.status_code,200)
        self.assertTemplateUsed(response,'accounts/user_registration.html')

    
    def test_valid_user_registration(self):
        response=self.client.post(reverse('user_registration'),{
            'username':'testuser',
            'email':'testuser@gmail.com',
            'password1':'StrongPassword123!',
            'password2':'StrongPassword123!'
        })

        self.assertEqual(response.status_code,302)
        self.assertTrue(User.objects.filter(username='testuser').exists())

    def test_invalid_user_registration(self):
        response=self.client.post(reverse('user_registration'),{
            'username':'',
            'email':'invalidemail',
            'password1':'pass',
            'password2':'different'

        })

        self.assertEqual(response.status_code,200)
        self.assertContains(response,"This field is required.")
        self.assertContains(response,"Enter a valid email address.")
        self.assertContains(response,"The two password fields didn’t match.")
    
    def test_registration_view_have_link_to_login_page(self):
        response=self.client.get(reverse('user_registration'))
        login_url=reverse('user_login')
        self.assertContains(response,f'href="{login_url}"')

class UserLoginViewTests(TestCase):
    def setUp(self):
        self.testuser=User.objects.create_user(username='testuser',password='testuser@123')

    def test_user_login_url_resolves_user_login_view(self):
        view=resolve('/login/')
        self.assertEqual(view.func.view_class,auth_views.LoginView)
    
    def test_login_page_uses_correct_template(self):
        response=self.client.get(reverse('user_login'))
        self.assertEqual(response.status_code,200)
        self.assertTemplateUsed(response,'accounts/user_login.html')

    def test_valid_user_login(self):
        response=self.client.post(reverse('user_login'),{
            'username':'testuser',
            'password':'testuser@123'
        })
        self.assertEqual(response.status_code, 302)
        self.assertIn('_auth_user_id',self.client.session)
    
    def test_invalid_user_login(self):
        response=self.client.post(reverse('user_login'),{
            'username':'user',
            'password':'user@123'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response,"Please enter a correct username and password. Note that both fields may be case-sensitive.")
        self.assertNotIn('_auth_user_id',self.client.session)
    
    def test_login_view_have_link_to_registration_page(self):
        response=self.client.get(reverse('user_login'))
        registration_url=reverse('user_registration')
        self.assertContains(response,f'href="{registration_url}"')
    
    def test_login_view_have_link_to_password_reset_page(self):
        response=self.client.get(reverse('user_login'))
        password_reset_url=reverse('password_reset')
        self.assertContains(response,f'href="{password_reset_url}"')

class PasswordResetViewTests(TestCase):

    def setUp(self):
        self.response=self.client.get(reverse('password_reset'))
    
    def test_password_reset_page_use_correct_template(self):
        self.assertEqual(self.response.status_code,200)
        self.assertTemplateUsed(self.response,'accounts/password_reset.html')

    def test_password_reset_url_resolves_password_reset_view(self):
        view=resolve('/password_reset/')
        self.assertEqual(view.func.view_class,auth_views.PasswordResetView)
    
    def test_password_reset_page_contains_form_and_csrf(self):
        form=self.response.context.get('form')
        self.assertIsInstance(form,PasswordResetForm)
        self.assertContains(self.response,'csrfmiddlewaretoken')

    def test_valid_password_reset(self):
        email='testuser@gmail.com'
        User.objects.create_user(username='testuser',email=email,password='testuser@123')
        response=self.client.post(reverse('password_reset'),{'email':email,})
        self.assertRedirects(response,reverse('password_reset_done'))
        self.assertEqual(1,len(mail.outbox))
    
    def test_invalid_password_reset(self):
        response=self.client.post(reverse('password_reset'),{'email':'unknown@gmail.com',})
        self.assertRedirects(response,reverse('password_reset_done'))
        self.assertEqual(0,len(mail.outbox))

class PasswordResetDoneViewTests(TestCase):
    def setUp(self):
        self.response=self.client.get(reverse('password_reset_done'))
    
    def test_view_use_correct_template(self):
        self.assertEqual(self.response.status_code, 200)
        self.assertTemplateUsed(self.response,'accounts/password_reset_done.html')
    
    def test_page_resloves_correct_view(self):
        view=resolve('/password_reset/done/')
        self.assertEqual(view.func.view_class,auth_views.PasswordResetDoneView)
    
    def test_page_contains_exact_content(self):
        self.assertContains(self.response,"Check your email for a link to reset your password. If it doesn't appear within a few minutes, check your spam folder.")


class PasswordResetConfirmViewTests(TestCase):
    def setUp(self):
        self.user=User.objects.create_user(username='john',email='john@gmail.com',password='123abc')
        self.uid=urlsafe_base64_encode(force_bytes(self.user.pk))
        self.token=default_token_generator.make_token(self.user)
        self.valid_url=reverse('password_reset_confirm',kwargs={'uidb64':self.uid,'token':self.token})
        self.invalid_url = reverse('password_reset_confirm', kwargs={'uidb64': 'invalid_uid', 'token': 'invalid_token'})
    
    def test_password_confirm_page_use_correct_template(self):
        response=self.client.get(self.valid_url,follow=True)
        self.assertEqual(response.status_code,200)
        self.assertTemplateUsed(response,'accounts/password_reset_confirm.html')

    def test_password_confirm_url_resolves_password_confirm_view(self):
        view=resolve('/password_reset/<uidb64>/<token>/')
        self.assertEqual(view.func.view_class,auth_views.PasswordResetConfirmView)
    
    def test_password_confirm_page_contains_csrf(self):
        response=self.client.get(self.valid_url,follow=True)
        self.assertContains(response,'csrfmiddlewaretoken')
    
    def test_password_confirm_page_contains_input(self):
        response=self.client.get(self.valid_url,follow=True)
        self.assertContains(response,'<input',3)
        self.assertContains(response, 'type="password"',2)
    
    def test_password_cofirm_invalid_link(self):
        response=self.client.get(self.invalid_url)
        self.assertEqual(response.status_code,200)
        self.assertContains(response,"It looks like you clicked on an invalid password reset link.")

    def test_valid_password_confirm(self):
        response = self.client.post(
            self.valid_url,
            {'new_password1': 'new_secure_password123', 'new_password2': 'new_secure_password123'},
            follow=True
        )
        set_password_url = f"/password_reset/{self.uid}/set-password/"
        self.assertRedirects(response, set_password_url)

        response = self.client.post(
        set_password_url,
        {'new_password1': 'new_secure_password123', 'new_password2': 'new_secure_password123'},
        follow=True
        )
        self.assertRedirects(response, reverse('password_reset_complete'))
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('new_secure_password123'))

class PasswordResetCompleteViewTests(TestCase):
    def setUp(self):
        self.response=self.client.get(reverse('password_reset_complete'))
    
    def test_view_use_correct_template(self):
        self.assertEqual(self.response.status_code, 200)
        self.assertTemplateUsed(self.response,'accounts/password_reset_complete.html')
    
    def test_page_resloves_correct_view(self):
        view=resolve('/password_reset/complete/')
        self.assertEqual(view.func.view_class,auth_views.PasswordResetCompleteView)
    
    def test_page_contains_exact_content(self):
        self.assertContains(self.response,"You have successfully changed your password! You may now proceed to log in.")

    
class PasswordChangeViewTests(TestCase):

    def setUp(self):
        self.testuser=User.objects.create_user(username='testuser',password='testuser@123')
        self.client.login(username='testuser',password='testuser@123')

    def test_passwordchange_redirects_anonymous_user(self):
        self.client.logout()
        response=self.client.get(reverse('password_change'))
        self.assertRedirects(response,f"{reverse('user_login')}?next={reverse('password_change')}")
    
    def test_view_use_correct_template(self):
        response=self.client.get(reverse('password_change'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response,'accounts/password_change.html')
    
    def test_page_resloves_correct_view(self):
        view=resolve('/password_change/')
        self.assertEqual(view.func.view_class,auth_views.PasswordChangeView)

    def test_invalid_password_change(self):
         response=self.client.post(reverse('password_change'),{
            'old_password': '',
            'new_password1': 'new_pass',
            'new_password2': 'new_password',
         })

         self.assertEqual(response.status_code,200)
         form=response.context.get('form')
         self.assertTrue(form.errors)
         self.testuser.refresh_from_db()
         self.assertTrue(self.testuser.check_password('testuser@123'))

    def test_valid_password_change(self):
         response=self.client.post(reverse('password_change'),{
            'old_password': 'testuser@123',
            'new_password1': 'newuser@123',
            'new_password2': 'newuser@123',
         },follow=True)
         self.assertRedirects(response,reverse('password_change_done'))
         self.assertContains(response,"You have successfully changed your password!")
         self.testuser.refresh_from_db()
         self.assertTrue(self.testuser.check_password('newuser@123'))

class UserProfileViewTests(TestCase):
    def setUp(self):
        self.testuser=User.objects.create_user(username='testuser',password='testuser@123')
        self.client.login(username='testuser',password='testuser@123')
        self.response=self.client.get(reverse('user_profile'))
    
    def test_view_use_correct_template(self):
        self.assertEqual(self.response.status_code, 200)
        self.assertTemplateUsed(self.response,'accounts/user_profile.html')
    
    def test_page_resloves_correct_view(self):
        view=resolve('/profile/')
        self.assertEqual(view.func.view_class,UserProfileUpdateView)
    
    def test_invalid_access_redirects_to_login(self):
        self.client.logout()
        response=self.client.get(reverse('user_profile'))
        self.assertRedirects(response,f"{reverse('user_login')}?next={reverse('user_profile')}")
    
    def test_form_input(self):
        self.assertContains(self.response,'<input',5)
        self.assertContains(self.response, 'type="text"',2)
        self.assertContains(self.response, 'type="email"',1)
    

         

         


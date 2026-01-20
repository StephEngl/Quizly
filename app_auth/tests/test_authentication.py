from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from django.urls import reverse
from django.contrib.auth.models import User

class AuthenticationTests(APITestCase):
    """Test suite for user authentication functionality.
    
    Tests registration, login, logout, and token refresh endpoints
    using HttpOnly cookies for JWT token management.
    """
    def setUp(self):
        """Set up test client and URL endpoints for authentication tests."""
        self.client = APIClient()
        self.register_url = reverse('register')
        self.login_url = reverse('token_obtain_pair')
        self.logout_url = reverse('token_logout')
        self.refresh_url = reverse('token_refresh')
        
        self.user_data = {
            'username': 'testuser',
            'email': 'test@quiz.de',
            'password': 'testpass123',
            'confirmed_password': 'testpass123'
        }


    def get_login_data(self, username=None, password=None):
        """Helper method to get login data.
        
        Args:
            username: Optional username override.
            password: Optional password override.
            
        Returns:
            dict: Login credentials dictionary.
        """
        return {
            'username': username or self.user_data['username'],
            'password': password or self.user_data['password']
        }


    def create_user(self):
        """Helper method to create a test user.
        
        Returns:
            User: Created user instance.
        """
        return User.objects.create_user(
            username=self.user_data['username'],
            email=self.user_data['email'],
            password=self.user_data['password']
        )


    def create_and_login_user(self):
        """Helper method to create a user and log them in.
        
        Creates a user, performs login, and sets authentication cookies
        on the test client for subsequent authenticated requests.
        
        Returns:
            tuple: (user_instance, login_response)
        """
        user = self.create_user()
        
        login_data = self.get_login_data()
        
        login_response = self.client.post(self.login_url, login_data, format='json')
        
        if login_response.status_code == status.HTTP_200_OK:
            refresh_token = login_response.cookies['refresh_token'].value
            access_token = login_response.cookies['access_token'].value
            
            self.client.cookies['refresh_token'] = refresh_token
            self.client.cookies['access_token'] = access_token
            
            self.client.force_authenticate(user=user)
        
        return user, login_response


    def test_user_registration(self):
        """Test successful user registration."""
        response = self.client.post(self.register_url, self.user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['detail'], 'User created successfully!')
        
        self.assertTrue(User.objects.filter(username='testuser').exists())


    def test_user_login(self):
        """Test successful user login with JWT cookie creation."""
        self.create_user()
        login_data = self.get_login_data()
        
        response = self.client.post(self.login_url, login_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['detail'], 'Login successfully!')
        self.assertIn('user', response.data)
        
        self.assertIn('refresh_token', response.cookies)
        self.assertIn('access_token', response.cookies)
        
        refresh_cookie = response.cookies['refresh_token']
        access_cookie = response.cookies['access_token']
        
        self.assertTrue(refresh_cookie['httponly'])
        self.assertTrue(access_cookie['httponly'])


    def test_user_login_invalid_credentials(self):
        """Test login failure with invalid credentials."""
        login_data = self.get_login_data(username='nonexistent', password='wrongpass')
        
        response = self.client.post(self.login_url, login_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


    def test_user_logout(self):
        """Test successful user logout and cookie deletion."""
        user, login_response = self.create_and_login_user()
        self.assertEqual(login_response.status_code, status.HTTP_200_OK)

        logout_response = self.client.post(self.logout_url, format='json')
        self.assertEqual(logout_response.status_code, status.HTTP_200_OK)
        self.assertIn('Log-Out successfully!', logout_response.data['detail'])


    def test_logout_without_authentication(self):
        """Test logout attempt without being authenticated."""
        response = self.client.post(self.logout_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


    def test_token_refresh(self):
        """Test successful JWT token refresh using HttpOnly cookies."""
        user, login_response = self.create_and_login_user()
        self.assertEqual(login_response.status_code, status.HTTP_200_OK)
        
        refresh_response = self.client.post(self.refresh_url, format='json')
        self.assertEqual(refresh_response.status_code, status.HTTP_200_OK)
        self.assertEqual(refresh_response.data['detail'], 'Token refreshed')
        self.assertIn('access', refresh_response.data)


    def test_token_refresh_without_refresh_token(self):
        """Test token refresh failure when no refresh token is provided."""
        user = self.create_user()
        
        self.client.force_authenticate(user=user)
        response = self.client.post(self.refresh_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn('error', response.data)


    def test_token_refresh_invalid_token(self):
        """Test token refresh failure with invalid refresh token."""
        user, login_response = self.create_and_login_user()
        self.assertEqual(login_response.status_code, status.HTTP_200_OK)
        
        self.client.cookies['refresh_token'] = 'invalid_token'
        
        response = self.client.post(self.refresh_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn('error', response.data)
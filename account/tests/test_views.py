from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from account.models import User

class SignUpViewTest(APITestCase):
    def test_signup_view(self):
        url = reverse('signup')
        data = {'username': 'testuser', 'password': 'testpassword', 'is_active': True}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(User.objects.get().username, 'testuser')

    def test_signup_view_invalid_data(self):
        url = reverse('signup')
        data = {'username': 'testuser', 'password': '', 'is_active': True}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(User.objects.count(), 0)


class LoginViewTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword', is_active=True)

    def test_login_view(self):
        url = reverse('token_obtain_pair')
        data = {'username': 'testuser', 'password': 'testpassword'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_login_view_invalid_credentials(self):
        url = reverse('token_obtain_pair')
        data = {'username': 'testuser', 'password': 'wrongpassword'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
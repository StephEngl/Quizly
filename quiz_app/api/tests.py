# from django.test import TestCase
# from rest_framework import status
# from rest_framework.response import Response
# from rest_framework.test import APITestCase, APIClient
# from django.urls import reverse

# class QuizAppTests(APITestCase):
#     def setUp(self):
#         self.client = APIClient()
#         self.quiz_url = reverse('quiz-list')  # Assuming you have a view named 'quiz-list'

#     def test_get_quizzes_unauthenticated(self):
#         response = self.client.get(self.quiz_url)
#         self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

#     def test_get_quizzes_authenticated(self):
#         # Create and authenticate a user
#         from django.contrib.auth.models import User
#         user = User.objects.create_user(username='testuser', password='testpass')
#         self.client.login(username='testuser', password='testpass')

#         response = self.client.get(self.quiz_url)
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertIsInstance(response.data, list)  # Assuming the response is a list of quizzes
    
#     def test_create_quiz(self):
#         from django.contrib.auth.models import User
#         user = User.objects.create_user(username='testuser', password='testpass')
#         self.client.login(username='testuser', password='testpass')

#         quiz_data = {
#             'title': 'Sample Quiz',
#             'description': 'This is a sample quiz description.'
#         }
#         response = self.client.post(self.quiz_url, quiz_data, format='json')
#         self.assertEqual(response.status_code, status.HTTP_201_CREATED)
#         self.assertEqual(response.data['title'], quiz_data['title'])
#         self.assertEqual(response.data['description'], quiz_data['description'])
    


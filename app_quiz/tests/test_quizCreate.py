import warnings
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from django.urls import reverse
from django.contrib.auth import get_user_model
from unittest.mock import patch

from ..models import Quiz, Question

User = get_user_model()


class QuizCreateTests(APITestCase):
    def setUp(self):
        warnings.filterwarnings("ignore", message="FP16 is not supported on CPU")
        warnings.filterwarnings("ignore", category=UserWarning)

        self.client = APIClient()
        self.create_quiz_url = reverse('create_quiz_from_url')

        self.user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'testpass123'
        }

        self.mock_transcript = "This is a sample transcript about Python programming basics."
        self.mock_quiz_data = {
            'title': 'Python Basics Quiz',
            'description': 'A comprehensive quiz about Python programming fundamentals',
            'questions': [
                {
                    'question_title': f'What is Python question {i}?',
                    'question_options': ['Option A', 'Option B', 'Option C', 'Option D'],
                    'answer': ['Option A', 'Option B', 'Option C', 'Option D'][i % 4]
                } for i in range(1, 11)
            ]
        }


    def setup_mocks(self, mock_download_transcribe, mock_generate_quiz):
        """Helper method to configure standard mock behavior"""
        mock_download_transcribe.return_value = (
            self.mock_transcript, "Sample Video Title")
        mock_generate_quiz.return_value = self.mock_quiz_data
        return mock_download_transcribe, mock_generate_quiz


    def create_user(self):
        return User.objects.create_user(**self.user_data)


    def authenticate_user(self):
        user = self.create_user()
        self.client.force_authenticate(user=user)
        return user


    def get_quiz_data(self):
        return {'url': 'https://www.youtube.com/watch?v=dQw4w9WgXcQ'}

    # ========= CORE STATUS CODE TESTS =========
    
    @patch('app_quiz.api.utils.generate_quiz_from_transcript')
    @patch('app_quiz.api.views.download_and_transcribe')
    def test_create_quiz_success_201(self, mock_download_transcribe, mock_generate_quiz):
        """Test creating a quiz returns 201 and creates database records"""
        self.setup_mocks(mock_download_transcribe, mock_generate_quiz)

        user = self.authenticate_user()
        quiz_data = self.get_quiz_data()

        response = self.client.post(self.create_quiz_url, quiz_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['video_url'], quiz_data['url'])
        
        # Verify database creation
        self.assertEqual(Quiz.objects.count(), 1)
        self.assertEqual(Question.objects.count(), 10)
        
        quiz = Quiz.objects.first()
        self.assertEqual(quiz.video_url, quiz_data['url'])
        self.assertEqual(quiz.owner, user)

        # Verify external services were called correctly
        mock_download_transcribe.assert_called_once_with(quiz_data['url'])
        mock_generate_quiz.assert_called_once_with(self.mock_transcript)


    def test_create_quiz_unauthorized_401(self):
        """Test creating quiz without authentication returns 401"""
        quiz_data = self.get_quiz_data()
        response = self.client.post(self.create_quiz_url, quiz_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


    def test_create_quiz_missing_url_400(self):
        """Test creating quiz without URL returns 400"""
        self.authenticate_user()
        response = self.client.post(self.create_quiz_url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('url', response.data)


    def test_create_quiz_invalid_url_400(self):
        """Test creating quiz with invalid URL returns 400"""
        self.authenticate_user()
        quiz_data = {'url': 'not-a-valid-url'}
        response = self.client.post(self.create_quiz_url, quiz_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('url', response.data)

    # ========= RESPONSE STRUCTURE TESTS =========

    @patch('app_quiz.api.utils.generate_quiz_from_transcript')
    @patch('app_quiz.api.views.download_and_transcribe')
    def test_response_has_required_fields(self, mock_download_transcribe, mock_generate_quiz):
        """Test that response contains all required fields per API spec"""
        self.setup_mocks(mock_download_transcribe, mock_generate_quiz)
        self.authenticate_user()

        response = self.client.post(self.create_quiz_url, self.get_quiz_data(), format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Quiz fields from API spec
        required_quiz_fields = ['id', 'title', 'description', 'created_at', 'updated_at', 'video_url', 'questions']
        for field in required_quiz_fields:
            self.assertIn(field, response.data, f"Field '{field}' missing in response")

        # Question fields from API spec  
        self.assertEqual(len(response.data['questions']), 10)
        required_question_fields = ['id', 'question_title', 'question_options', 'answer', 'created_at', 'updated_at']
        for question in response.data['questions']:
            for field in required_question_fields:
                self.assertIn(field, question, f"Field '{field}' missing in question")


    @patch('app_quiz.api.utils.generate_quiz_from_transcript')
    @patch('app_quiz.api.views.download_and_transcribe')
    def test_response_field_types(self, mock_download_transcribe, mock_generate_quiz):
        """Test that response fields have correct data types per API spec"""
        self.setup_mocks(mock_download_transcribe, mock_generate_quiz)
        self.authenticate_user()

        response = self.client.post(self.create_quiz_url, self.get_quiz_data(), format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Quiz field types
        self.assertIsInstance(response.data['id'], int)
        self.assertIsInstance(response.data['title'], str)
        self.assertIsInstance(response.data['description'], str)
        self.assertIsInstance(response.data['created_at'], str)
        self.assertIsInstance(response.data['updated_at'], str)
        self.assertIsInstance(response.data['video_url'], str)
        self.assertIsInstance(response.data['questions'], list)

        # Question field types
        for question in response.data['questions']:
            self.assertIsInstance(question['id'], int)
            self.assertIsInstance(question['question_title'], str)
            self.assertIsInstance(question['question_options'], list)
            self.assertIsInstance(question['answer'], str)
            self.assertIsInstance(question['created_at'], str)
            self.assertIsInstance(question['updated_at'], str)
            
            # Question options should have 4 options as shown in API spec
            self.assertEqual(len(question['question_options']), 4)


    @patch('app_quiz.api.utils.generate_quiz_from_transcript')
    @patch('app_quiz.api.views.download_and_transcribe')
    def test_serializer_datetime_format(self, mock_download_transcribe, mock_generate_quiz):
        """Test that datetime fields are in correct ISO format"""
        self.setup_mocks(mock_download_transcribe, mock_generate_quiz)

        self.authenticate_user()
        quiz_data = self.get_quiz_data()

        response = self.client.post(
            self.create_quiz_url, quiz_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        created_at = response.data['created_at']
        updated_at = response.data['updated_at']

        import re
        datetime_pattern = r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d+Z'

        self.assertRegex(created_at, datetime_pattern,
                         "created_at not in correct ISO format")
        self.assertRegex(updated_at, datetime_pattern,
                         "updated_at not in correct ISO format")


    @patch('app_quiz.api.utils.generate_quiz_from_transcript')
    @patch('app_quiz.api.views.download_and_transcribe')
    def test_serializer_read_only_fields(self, mock_download_transcribe, mock_generate_quiz):
        """Test that read-only fields are not affected by input"""
        self.setup_mocks(mock_download_transcribe, mock_generate_quiz)

        self.authenticate_user()
        quiz_data = self.get_quiz_data()

        quiz_data['id'] = 999
        quiz_data['created_at'] = '2020-01-01T00:00:00.000Z'
        quiz_data['updated_at'] = '2020-01-01T00:00:00.000Z'
        quiz_data['questions'] = [{'question_title': 'Should not be used'}]

        response = self.client.post(
            self.create_quiz_url, quiz_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.assertNotEqual(response.data['id'], 999)
        self.assertNotEqual(
            response.data['created_at'], '2020-01-01T00:00:00.000Z')
        self.assertNotEqual(
            response.data['updated_at'], '2020-01-01T00:00:00.000Z')

        self.assertEqual(len(response.data['questions']), 10)
        self.assertNotEqual(
            response.data['questions'][0]['question_title'], 'Should not be used')


    @patch('app_quiz.api.utils.generate_quiz_from_transcript')
    @patch('app_quiz.api.views.download_and_transcribe')
    def test_serializer_writable_fields_only(self, mock_download_transcribe, mock_generate_quiz):
        """Test that only writable fields affect the created object"""
        self.setup_mocks(mock_download_transcribe, mock_generate_quiz)

        self.authenticate_user()
        quiz_data = self.get_quiz_data()

        response = self.client.post(
            self.create_quiz_url, quiz_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.assertEqual(response.data['video_url'], quiz_data['url'])

        self.assertIsNotNone(response.data['id'])
        self.assertIsNotNone(response.data['title'])
        self.assertIsNotNone(response.data['description'])
        self.assertIsNotNone(response.data['created_at'])
        self.assertIsNotNone(response.data['updated_at'])
        self.assertEqual(len(response.data['questions']), 10)

import warnings
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from django.urls import reverse
from django.contrib.auth import get_user_model
from unittest.mock import patch, MagicMock

from ..models import Quiz, Question

User = get_user_model()


class QuizCreateTests(APITestCase):
    def setUp(self):
        # Suppress all warnings in tests
        warnings.filterwarnings("ignore", message="FP16 is not supported on CPU")
        warnings.filterwarnings("ignore", category=UserWarning)
        
        self.client = APIClient()
        self.create_quiz_url = reverse(
            'create_quiz_from_url')  # /api/createQuiz/

        # Test user data
        self.user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'testpass123'
        }
        
        # Mock data für externe Services
        self.mock_transcript = "This is a sample transcript about Python programming basics."
        self.mock_quiz_data = {
            'title': 'Python Basics Quiz',
            'description': 'A comprehensive quiz about Python programming fundamentals',
            'questions': [
                {
                    'question_title': f'What is Python question {i}?',
                    'question_options': ['Option A', 'Option B', 'Option C', 'Option D'],
                    'answer': ['Option A', 'Option B', 'Option C', 'Option D'][i % 4]  # Diverse answers
                } for i in range(1, 11)
            ]
        }

    def create_user(self):
        """Helper method to create a test user"""
        return User.objects.create_user(**self.user_data)

    def authenticate_user(self):
        """Helper method to create and authenticate a user"""
        user = self.create_user()
        self.client.force_authenticate(user=user)
        return user

    def get_quiz_data(self):
        """Helper method to get valid quiz data"""
        return {
            'url': 'https://www.youtube.com/watch?v=dQw4w9WgXcQ'
        }

    # ========= FUNKTIONIERENDEN MOCKS =========
    @patch('app_quiz.api.views.generate_quiz_from_transcript')  # Mock in der View!
    @patch('app_quiz.api.views.download_and_transcribe')       # Mock in der View!
    def test_create_quiz_authenticated(self, mock_download_transcribe, mock_generate_quiz):
        """Test creating a quiz with authenticated user (View-Level Mocks)"""
        # Setup mocks - download_and_transcribe returns (transcript, title)
        mock_download_transcribe.return_value = (self.mock_transcript, "Sample Video Title")
        mock_generate_quiz.return_value = self.mock_quiz_data
        
        self.authenticate_user()
        quiz_data = self.get_quiz_data()

        response = self.client.post(
            self.create_quiz_url, quiz_data, format='json')

        # Debug output if test fails
        if response.status_code != 201:
            print(f"❌ Response status: {response.status_code}")
            print(f"❌ Response data: {response.data}")
            print(f"❌ Mock download called: {mock_download_transcribe.called}")
            print(f"❌ Mock generate called: {mock_generate_quiz.called}")
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['video_url'], quiz_data['url'])
        self.assertIsNotNone(response.data['title'])
        self.assertIsNotNone(response.data['description'])

        # Check if quiz was actually created in database
        self.assertTrue(Quiz.objects.filter(video_url=quiz_data['url']).exists())
        
        # Verify mocks were called
        mock_download_transcribe.assert_called_once_with(quiz_data['url'])
        mock_generate_quiz.assert_called_once_with(self.mock_transcript)

    def test_create_quiz_unauthenticated(self):
        """Test creating a quiz without authentication"""
        quiz_data = self.get_quiz_data()

        response = self.client.post(
            self.create_quiz_url, quiz_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_quiz_missing_url(self):
        """Test creating a quiz without video_url"""
        self.authenticate_user()
        quiz_data = {}

        response = self.client.post(
            self.create_quiz_url, quiz_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('url', response.data)

    def test_create_quiz_invalid_video_url(self):
        """Test creating a quiz with invalid video URL"""
        self.authenticate_user()
        quiz_data = self.get_quiz_data()
        quiz_data = {'url': 'not-a-valid-url'}

        response = self.client.post(
            self.create_quiz_url, quiz_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('url', response.data)

    @patch('app_quiz.api.views.generate_quiz_from_transcript')
    @patch('app_quiz.api.views.download_and_transcribe')
    def test_create_quiz_database_creation(self, mock_download_transcribe, mock_generate_quiz):
        """Test that quiz is actually created in database with correct data"""
        # Setup mocks
        mock_download_transcribe.return_value = (self.mock_transcript, "Sample Video Title")
        mock_generate_quiz.return_value = self.mock_quiz_data
        
        self.authenticate_user()
        quiz_data = self.get_quiz_data()

        # Check no quiz exists before
        self.assertEqual(Quiz.objects.count(), 0)

        response = self.client.post(
            self.create_quiz_url, quiz_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Check quiz was created
        self.assertEqual(Quiz.objects.count(), 1)

        # Check quiz data is correct
        quiz = Quiz.objects.first()
        self.assertEqual(quiz.video_url, quiz_data['url'])
        self.assertIsNotNone(quiz.title)
        self.assertIsNotNone(quiz.description)
        self.assertIsNotNone(quiz.created_at)
        self.assertIsNotNone(quiz.updated_at)

    @patch('app_quiz.api.views.generate_quiz_from_transcript')
    @patch('app_quiz.api.views.download_and_transcribe')
    def test_serializer_fields_present(self, mock_download_transcribe, mock_generate_quiz):
        """Test that all required fields are present in response"""
        # Setup mocks
        mock_download_transcribe.return_value = (self.mock_transcript, "Sample Video Title")
        mock_generate_quiz.return_value = self.mock_quiz_data
        
        self.authenticate_user()
        quiz_data = self.get_quiz_data()

        response = self.client.post(
            self.create_quiz_url, quiz_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Check all required fields are present
        expected_fields = ['id', 'title', 'description',
                           'created_at', 'updated_at', 'video_url', 'questions']
        for field in expected_fields:
            self.assertIn(field, response.data,
                          f"Field '{field}' missing in response")

    @patch('app_quiz.api.views.generate_quiz_from_transcript')
    @patch('app_quiz.api.views.download_and_transcribe')
    def test_serializer_field_order(self, mock_download_transcribe, mock_generate_quiz):
        """Test that fields are returned in correct order"""
        # Setup mocks
        mock_download_transcribe.return_value = (self.mock_transcript, "Sample Video Title")
        mock_generate_quiz.return_value = self.mock_quiz_data
        
        self.authenticate_user()
        quiz_data = self.get_quiz_data()

        response = self.client.post(
            self.create_quiz_url, quiz_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Check field order matches serializer definition
        expected_order = ['id', 'title', 'description',
                          'created_at', 'updated_at', 'video_url', 'questions']
        actual_fields = list(response.data.keys())

        self.assertEqual(actual_fields, expected_order,
                         f"Field order mismatch. Expected: {expected_order}, Got: {actual_fields}")

    @patch('app_quiz.api.views.generate_quiz_from_transcript')
    @patch('app_quiz.api.views.download_and_transcribe')
    def test_serializer_field_types(self, mock_download_transcribe, mock_generate_quiz):
        """Test that fields have correct data types"""
        # Setup mocks
        mock_download_transcribe.return_value = (self.mock_transcript, "Sample Video Title")
        mock_generate_quiz.return_value = self.mock_quiz_data
        
        self.authenticate_user()
        quiz_data = self.get_quiz_data()

        response = self.client.post(
            self.create_quiz_url, quiz_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Check field types
        self.assertIsInstance(response.data['id'], int)
        self.assertIsInstance(response.data['title'], str)
        self.assertIsInstance(response.data['description'], str)
        # ISO datetime string
        self.assertIsInstance(response.data['created_at'], str)
        # ISO datetime string
        self.assertIsInstance(response.data['updated_at'], str)
        self.assertIsInstance(response.data['video_url'], str)
        self.assertIsInstance(response.data['questions'], list)

    @patch('app_quiz.api.views.generate_quiz_from_transcript')
    @patch('app_quiz.api.views.download_and_transcribe')
    def test_serializer_questions_array_generated(self, mock_download_transcribe, mock_generate_quiz):
        """Test that 10 questions are automatically generated for new quiz"""
        # Setup mocks
        mock_download_transcribe.return_value = (self.mock_transcript, "Sample Video Title")
        mock_generate_quiz.return_value = self.mock_quiz_data
        
        self.authenticate_user()
        quiz_data = self.get_quiz_data()

        response = self.client.post(
            self.create_quiz_url, quiz_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Questions should contain exactly 10 generated questions
        self.assertEqual(len(response.data['questions']), 10)
        self.assertIsInstance(response.data['questions'], list)

    @patch('app_quiz.api.views.generate_quiz_from_transcript')
    @patch('app_quiz.api.views.download_and_transcribe')
    def test_generated_questions_structure(self, mock_download_transcribe, mock_generate_quiz):
        """Test that generated questions have correct structure"""
        # Setup mocks
        mock_download_transcribe.return_value = (self.mock_transcript, "Sample Video Title")
        mock_generate_quiz.return_value = self.mock_quiz_data
        
        self.authenticate_user()
        quiz_data = self.get_quiz_data()

        response = self.client.post(
            self.create_quiz_url, quiz_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(response.data['questions']), 10)

        for i, question in enumerate(response.data['questions']):
            # Check all required fields are present
            expected_fields = ['id', 'question_title', 'question_options', 'answer', 'created_at', 'updated_at']
            for field in expected_fields:
                self.assertIn(field, question,
                            f"Field '{field}' missing in question {i+1}")

            # Check field types
            self.assertIsInstance(question['id'], int)
            self.assertIsInstance(question['question_title'], str)
            self.assertIsInstance(question['question_options'], list)
            self.assertIsInstance(question['answer'], str)
            self.assertIsInstance(question['created_at'], str)
            self.assertIsInstance(question['updated_at'], str)

    @patch('app_quiz.api.views.generate_quiz_from_transcript')
    @patch('app_quiz.api.views.download_and_transcribe')
    def test_generated_questions_not_empty(self, mock_download_transcribe, mock_generate_quiz):
        """Test that generated questions contain actual content"""
        # Setup mocks
        mock_download_transcribe.return_value = (self.mock_transcript, "Sample Video Title")
        mock_generate_quiz.return_value = self.mock_quiz_data
        
        self.authenticate_user()
        quiz_data = self.get_quiz_data()

        response = self.client.post(
            self.create_quiz_url, quiz_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(response.data['questions']), 10)

        for i, question in enumerate(response.data['questions']):
            # Check content is not empty
            self.assertNotEqual(question['question_title'].strip(), '',
                              f"Question {i+1} title is empty")
            self.assertTrue(len(question['question_options']) >= 2,
                          f"Question {i+1} should have at least 2 options")
            self.assertIn(question['answer'], question['question_options'],
                        f"Question {i+1} answer should be in options")

    @patch('app_quiz.api.views.generate_quiz_from_transcript')
    @patch('app_quiz.api.views.download_and_transcribe')
    def test_generated_questions_database_creation(self, mock_download_transcribe, mock_generate_quiz):
        """Test that questions are actually created in database"""
        # Setup mocks
        mock_download_transcribe.return_value = (self.mock_transcript, "Sample Video Title")
        mock_generate_quiz.return_value = self.mock_quiz_data
        
        self.authenticate_user()
        quiz_data = self.get_quiz_data()

        # Check no questions exist before
        self.assertEqual(Question.objects.count(), 0)

        response = self.client.post(
            self.create_quiz_url, quiz_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Check 10 questions were created in database
        self.assertEqual(Question.objects.count(), 10)

        # Check questions are linked to the quiz
        quiz = Quiz.objects.first()
        quiz_questions = quiz.questions.all()
        self.assertEqual(len(quiz_questions), 10)

        # Check question data matches response
        for db_question, response_question in zip(quiz_questions, response.data['questions']):
            self.assertEqual(db_question.id, response_question['id'])
            self.assertEqual(db_question.question_title, response_question['question_title'])
            self.assertEqual(db_question.question_options, response_question['question_options'])
            self.assertEqual(db_question.answer, response_question['answer'])
            self.assertIsNotNone(response_question['created_at'])
            self.assertIsNotNone(response_question['updated_at'])

    @patch('app_quiz.api.views.generate_quiz_from_transcript')
    @patch('app_quiz.api.views.download_and_transcribe')
    def test_questions_have_multiple_choice_format(self, mock_download_transcribe, mock_generate_quiz):
        """Test that generated questions follow multiple choice format"""
        # Setup mocks
        mock_download_transcribe.return_value = (self.mock_transcript, "Sample Video Title")
        mock_generate_quiz.return_value = self.mock_quiz_data
        
        self.authenticate_user()
        quiz_data = self.get_quiz_data()

        response = self.client.post(
            self.create_quiz_url, quiz_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(response.data['questions']), 10)

        for i, question in enumerate(response.data['questions']):
            options = question['question_options']

            # Should have 4 options (typical multiple choice)
            self.assertEqual(len(options), 4,
                             f"Question {i+1} should have exactly 4 options")

            # All options should be unique
            self.assertEqual(len(options), len(set(options)),
                             f"Question {i+1} has duplicate options")

            # Options should be reasonable length (not too short/long)
            for j, option in enumerate(options):
                self.assertGreaterEqual(len(option.strip()), 1,
                                        f"Question {i+1}, option {j+1} too short")
                self.assertLessEqual(len(option.strip()), 100,
                                     f"Question {i+1}, option {j+1} too long")

    @patch('app_quiz.api.views.generate_quiz_from_transcript')
    @patch('app_quiz.api.views.download_and_transcribe')
    def test_questions_are_diverse(self, mock_download_transcribe, mock_generate_quiz):
        """Test that generated questions are not identical"""
        # Setup mocks
        mock_download_transcribe.return_value = (self.mock_transcript, "Sample Video Title")
        mock_generate_quiz.return_value = self.mock_quiz_data
        
        self.authenticate_user()
        quiz_data = self.get_quiz_data()

        response = self.client.post(
            self.create_quiz_url, quiz_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(response.data['questions']), 10)

        questions = response.data['questions']
        question_titles = [q['question_title'] for q in questions]

        # All question titles should be unique
        self.assertEqual(len(question_titles), len(set(question_titles)),
                         "Questions should have unique titles")

        # Questions should not all have the same answer
        answers = [q['answer'] for q in questions]
        unique_answers = set(answers)
        self.assertGreater(len(unique_answers), 1,
                           "Questions should have diverse answers")

    @patch('app_quiz.api.views.generate_quiz_from_transcript')
    @patch('app_quiz.api.views.download_and_transcribe')
    def test_quiz_creation_with_question_generation_timing(self, mock_download_transcribe, mock_generate_quiz):
        """Test that question generation doesn't cause timeout"""
        # Setup mocks
        mock_download_transcribe.return_value = (self.mock_transcript, "Sample Video Title")
        mock_generate_quiz.return_value = self.mock_quiz_data
        
        self.authenticate_user()
        quiz_data = self.get_quiz_data()

        import time
        start_time = time.time()

        response = self.client.post(
            self.create_quiz_url, quiz_data, format='json')

        end_time = time.time()
        duration = end_time - start_time

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(response.data['questions']), 10)

        # Should complete within reasonable time (adjust as needed)
        self.assertLess(duration, 30, "Question generation taking too long")

    @patch('app_quiz.api.views.generate_quiz_from_transcript')
    @patch('app_quiz.api.views.download_and_transcribe')
    def test_serializer_datetime_format(self, mock_download_transcribe, mock_generate_quiz):
        """Test that datetime fields are in correct ISO format"""
        # Setup mocks
        mock_download_transcribe.return_value = (self.mock_transcript, "Sample Video Title")
        mock_generate_quiz.return_value = self.mock_quiz_data
        
        self.authenticate_user()
        quiz_data = self.get_quiz_data()

        response = self.client.post(
            self.create_quiz_url, quiz_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Check datetime format (ISO format with T and Z)
        created_at = response.data['created_at']
        updated_at = response.data['updated_at']

        # Should be in ISO format like "2023-07-29T12:34:56.789Z"
        import re
        datetime_pattern = r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d+Z'

        self.assertRegex(created_at, datetime_pattern,
            "created_at not in correct ISO format")
        self.assertRegex(updated_at, datetime_pattern,
            "updated_at not in correct ISO format")

    @patch('app_quiz.api.views.generate_quiz_from_transcript')
    @patch('app_quiz.api.views.download_and_transcribe')
    def test_serializer_read_only_fields(self, mock_download_transcribe, mock_generate_quiz):
        """Test that read-only fields are not affected by input"""
        # Setup mocks
        mock_download_transcribe.return_value = (self.mock_transcript, "Sample Video Title")
        mock_generate_quiz.return_value = self.mock_quiz_data
        
        self.authenticate_user()
        quiz_data = self.get_quiz_data()

        # Try to set read-only fields
        quiz_data['id'] = 999
        quiz_data['created_at'] = '2020-01-01T00:00:00.000Z'
        quiz_data['updated_at'] = '2020-01-01T00:00:00.000Z'
        quiz_data['questions'] = [{'question_title': 'Should not be used'}]

        response = self.client.post(
            self.create_quiz_url, quiz_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Read-only fields should be auto-generated, not from input
        self.assertNotEqual(response.data['id'], 999)
        self.assertNotEqual(
            response.data['created_at'], '2020-01-01T00:00:00.000Z')
        self.assertNotEqual(
            response.data['updated_at'], '2020-01-01T00:00:00.000Z')

        # Questions should be auto-generated (10 questions), not from input
        self.assertEqual(len(response.data['questions']), 10)
        self.assertNotEqual(
            response.data['questions'][0]['question_title'], 'Should not be used')

    @patch('app_quiz.api.views.generate_quiz_from_transcript')
    @patch('app_quiz.api.views.download_and_transcribe')
    def test_serializer_writable_fields_only(self, mock_download_transcribe, mock_generate_quiz):
        """Test that only writable fields affect the created object"""
        # Setup mocks
        mock_download_transcribe.return_value = (self.mock_transcript, "Sample Video Title")
        mock_generate_quiz.return_value = self.mock_quiz_data
        
        self.authenticate_user()
        quiz_data = self.get_quiz_data()

        response = self.client.post(
            self.create_quiz_url, quiz_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Check that the video_url matches input URL
        self.assertEqual(response.data['video_url'], quiz_data['url'])
        
        # All other fields should be auto-generated
        self.assertIsNotNone(response.data['id'])
        self.assertIsNotNone(response.data['title'])  # Generated from video
        self.assertIsNotNone(response.data['description'])  # Generated from transcript
        self.assertIsNotNone(response.data['created_at'])
        self.assertIsNotNone(response.data['updated_at'])
        self.assertEqual(len(response.data['questions']), 10)  # Auto-generated

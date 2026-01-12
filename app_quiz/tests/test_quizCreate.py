from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from django.urls import reverse
from django.contrib.auth import get_user_model
from ..models import Quiz, Question

User = get_user_model()


class QuizCreateTests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.create_quiz_url = reverse(
            'create_quiz_from_url')  # /api/createQuiz/

        # Test user data
        self.user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'testpass123'
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
            'title': 'Test Quiz',
            'description': 'This is a test quiz description',
            'video_url': 'https://www.youtube.com/watch?v=example'
        }

    # def test_create_quiz_authenticated(self):
    #     """Test creating a quiz with authenticated user"""
    #     self.authenticate_user()
    #     quiz_data = self.get_quiz_data()

    #     response = self.client.post(
    #         self.create_quiz_url, quiz_data, format='json')

    #     self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    #     self.assertEqual(response.data['title'], quiz_data['title'])
    #     self.assertEqual(
    #         response.data['description'], quiz_data['description'])
    #     self.assertEqual(response.data['video_url'], quiz_data['video_url'])

    #     # Check if quiz was actually created in database
    #     self.assertTrue(Quiz.objects.filter(title=quiz_data['title']).exists())

    # def test_create_quiz_unauthenticated(self):
    #     """Test creating a quiz without authentication"""
    #     quiz_data = self.get_quiz_data()

    #     response = self.client.post(
    #         self.create_quiz_url, quiz_data, format='json')

    #     self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # def test_create_quiz_missing_title(self):
    #     """Test creating a quiz without title"""
    #     self.authenticate_user()
    #     quiz_data = self.get_quiz_data()
    #     del quiz_data['title']

    #     response = self.client.post(
    #         self.create_quiz_url, quiz_data, format='json')

    #     self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    #     self.assertIn('title', response.data)

    # def test_create_quiz_missing_description(self):
    #     """Test creating a quiz without description"""
    #     self.authenticate_user()
    #     quiz_data = self.get_quiz_data()
    #     del quiz_data['description']

    #     response = self.client.post(
    #         self.create_quiz_url, quiz_data, format='json')

    #     self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    #     self.assertIn('description', response.data)

    # def test_create_quiz_missing_video_url(self):
    #     """Test creating a quiz without video_url"""
    #     self.authenticate_user()
    #     quiz_data = self.get_quiz_data()
    #     del quiz_data['video_url']

    #     response = self.client.post(
    #         self.create_quiz_url, quiz_data, format='json')

    #     self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    #     self.assertIn('video_url', response.data)

    # def test_create_quiz_invalid_video_url(self):
    #     """Test creating a quiz with invalid video URL"""
    #     self.authenticate_user()
    #     quiz_data = self.get_quiz_data()
    #     quiz_data['video_url'] = 'not-a-valid-url'

    #     response = self.client.post(
    #         self.create_quiz_url, quiz_data, format='json')

    #     self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    #     self.assertIn('video_url', response.data)

    # def test_create_quiz_empty_title(self):
    #     """Test creating a quiz with empty title"""
    #     self.authenticate_user()
    #     quiz_data = self.get_quiz_data()
    #     quiz_data['title'] = ''

    #     response = self.client.post(
    #         self.create_quiz_url, quiz_data, format='json')

    #     self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    #     self.assertIn('title', response.data)

    # def test_create_quiz_empty_description(self):
    #     """Test creating a quiz with empty description"""
    #     self.authenticate_user()
    #     quiz_data = self.get_quiz_data()
    #     quiz_data['description'] = ''

    #     response = self.client.post(
    #         self.create_quiz_url, quiz_data, format='json')

    #     self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    #     self.assertIn('description', response.data)

    # def test_create_quiz_with_special_characters(self):
        """Test creating a quiz with special characters in title and description"""
        self.authenticate_user()
        quiz_data = self.get_quiz_data()
        quiz_data['title'] = 'Test Quiz: Äöü & Special Characters! @#$%'
        quiz_data['description'] = 'Description with émojis 🎯 and special chars ñ'

        response = self.client.post(
            self.create_quiz_url, quiz_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['title'], quiz_data['title'])
        self.assertEqual(
            response.data['description'], quiz_data['description'])

    # def test_create_quiz_very_long_title(self):
    #     """Test creating a quiz with very long title (over 200 chars)"""
    #     self.authenticate_user()
    #     quiz_data = self.get_quiz_data()
    #     quiz_data['title'] = 'A' * 300  # Over max_length=200

    #     response = self.client.post(
    #         self.create_quiz_url, quiz_data, format='json')

    #     self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    #     self.assertIn('title', response.data)

    # def test_create_quiz_database_creation(self):
    #     """Test that quiz is actually created in database with correct data"""
    #     self.authenticate_user()
    #     quiz_data = self.get_quiz_data()

    #     # Check no quiz exists before
    #     self.assertEqual(Quiz.objects.count(), 0)

    #     response = self.client.post(
    #         self.create_quiz_url, quiz_data, format='json')

    #     self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    #     # Check quiz was created
    #     self.assertEqual(Quiz.objects.count(), 1)

    #     # Check quiz data is correct
    #     quiz = Quiz.objects.first()
    #     self.assertEqual(quiz.title, quiz_data['title'])
    #     self.assertEqual(quiz.description, quiz_data['description'])
    #     self.assertEqual(quiz.video_url, quiz_data['video_url'])
    #     self.assertIsNotNone(quiz.created_at)
    #     self.assertIsNotNone(quiz.updated_at)

    # def test_serializer_fields_present(self):
    #     """Test that all required fields are present in response"""
    #     self.authenticate_user()
    #     quiz_data = self.get_quiz_data()

    #     response = self.client.post(
    #         self.create_quiz_url, quiz_data, format='json')

    #     self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    #     # Check all required fields are present
    #     expected_fields = ['id', 'title', 'description',
    #                        'created_at', 'updated_at', 'video_url', 'questions']
    #     for field in expected_fields:
    #         self.assertIn(field, response.data,
    #                       f"Field '{field}' missing in response")

    # def test_serializer_field_order(self):
    #     """Test that fields are returned in correct order"""
    #     self.authenticate_user()
    #     quiz_data = self.get_quiz_data()

    #     response = self.client.post(
    #         self.create_quiz_url, quiz_data, format='json')

    #     self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    #     # Check field order matches serializer definition
    #     expected_order = ['id', 'title', 'description',
    #                       'created_at', 'updated_at', 'video_url', 'questions']
    #     actual_fields = list(response.data.keys())

    #     self.assertEqual(actual_fields, expected_order,
    #                      f"Field order mismatch. Expected: {expected_order}, Got: {actual_fields}")

    # def test_serializer_field_types(self):
    #     """Test that fields have correct data types"""
    #     self.authenticate_user()
    #     quiz_data = self.get_quiz_data()

    #     response = self.client.post(
    #         self.create_quiz_url, quiz_data, format='json')

    #     self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    #     # Check field types
    #     self.assertIsInstance(response.data['id'], int)
    #     self.assertIsInstance(response.data['title'], str)
    #     self.assertIsInstance(response.data['description'], str)
    #     # ISO datetime string
    #     self.assertIsInstance(response.data['created_at'], str)
    #     # ISO datetime string
    #     self.assertIsInstance(response.data['updated_at'], str)
    #     self.assertIsInstance(response.data['video_url'], str)
    #     self.assertIsInstance(response.data['questions'], list)

    # def test_serializer_questions_array_generated(self):
    #     """Test that 10 questions are automatically generated for new quiz"""
    #     self.authenticate_user()
    #     quiz_data = self.get_quiz_data()

    #     response = self.client.post(
    #         self.create_quiz_url, quiz_data, format='json')

    #     self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    #     # Questions should contain exactly 10 generated questions
    #     self.assertEqual(len(response.data['questions']), 10)
    #     self.assertIsInstance(response.data['questions'], list)

    # def test_generated_questions_structure(self):
    #     """Test that generated questions have correct structure"""
    #     self.authenticate_user()
    #     quiz_data = self.get_quiz_data()

    #     response = self.client.post(
    #         self.create_quiz_url, quiz_data, format='json')

    #     self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    #     self.assertEqual(len(response.data['questions']), 10)

    #     for i, question in enumerate(response.data['questions']):
    #         # Check all required fields are present
    #         expected_fields = ['id', 'question_title',
    #                            'question_options', 'answer']
    #         for field in expected_fields:
    #             self.assertIn(field, question,
    #                           f"Field '{field}' missing in question {i+1}")

    #         # Check field types
    #         self.assertIsInstance(question['id'], int)
    #         self.assertIsInstance(question['question_title'], str)
    #         self.assertIsInstance(question['question_options'], list)
    #         self.assertIsInstance(question['answer'], str)

    # def test_generated_questions_not_empty(self):
    #     """Test that generated questions contain actual content"""
    #     self.authenticate_user()
    #     quiz_data = self.get_quiz_data()

    #     response = self.client.post(
    #         self.create_quiz_url, quiz_data, format='json')

    #     self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    #     self.assertEqual(len(response.data['questions']), 10)

    #     for i, question in enumerate(response.data['questions']):
    #         # Question title should not be empty
    #         self.assertNotEqual(question['question_title'].strip(), '',
    #                             f"Question {i+1} title is empty")
    #         self.assertGreater(len(question['question_title'].strip()), 5,
    #                            f"Question {i+1} title is too short")

    #         # Should have at least 2 options (preferably 4)
    #         self.assertGreaterEqual(len(question['question_options']), 2,
    #                                 f"Question {i+1} needs at least 2 options")

    #         # Each option should not be empty
    #         for j, option in enumerate(question['question_options']):
    #             self.assertNotEqual(option.strip(), '',
    #                                 f"Question {i+1}, option {j+1} is empty")

    #         # Answer should not be empty and should be one of the options
    #         self.assertNotEqual(question['answer'].strip(), '',
    #                             f"Question {i+1} answer is empty")
    #         self.assertIn(question['answer'], question['question_options'],
    #                       f"Question {i+1} answer not in options")

    # def test_generated_questions_database_creation(self):
    #     """Test that questions are actually created in database"""
    #     self.authenticate_user()
    #     quiz_data = self.get_quiz_data()

    #     # Check no questions exist before
    #     self.assertEqual(Question.objects.count(), 0)

    #     response = self.client.post(
    #         self.create_quiz_url, quiz_data, format='json')

    #     self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    #     # Check 10 questions were created in database
    #     self.assertEqual(Question.objects.count(), 10)

    #     # Check questions are linked to the quiz
    #     quiz = Quiz.objects.first()
    #     quiz_questions = quiz.questions.all()
    #     self.assertEqual(len(quiz_questions), 10)

    #     # Check question data matches response
    #     for db_question, response_question in zip(quiz_questions, response.data['questions']):
    #         self.assertEqual(db_question.id, response_question['id'])
    #         self.assertEqual(db_question.question_title,
    #                          response_question['question_title'])
    #         self.assertEqual(db_question.question_options,
    #                          response_question['question_options'])
    #         self.assertEqual(db_question.answer, response_question['answer'])

    # def test_questions_have_multiple_choice_format(self):
    #     """Test that generated questions follow multiple choice format"""
    #     self.authenticate_user()
    #     quiz_data = self.get_quiz_data()

    #     response = self.client.post(
    #         self.create_quiz_url, quiz_data, format='json')

    #     self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    #     self.assertEqual(len(response.data['questions']), 10)

    #     for i, question in enumerate(response.data['questions']):
    #         options = question['question_options']

    #         # Should have 4 options (typical multiple choice)
    #         self.assertEqual(len(options), 4,
    #                          f"Question {i+1} should have exactly 4 options")

    #         # All options should be unique
    #         self.assertEqual(len(options), len(set(options)),
    #                          f"Question {i+1} has duplicate options")

    #         # Options should be reasonable length (not too short/long)
    #         for j, option in enumerate(options):
    #             self.assertGreaterEqual(len(option.strip()), 1,
    #                                     f"Question {i+1}, option {j+1} too short")
    #             self.assertLessEqual(len(option.strip()), 100,
    #                                  f"Question {i+1}, option {j+1} too long")

    # def test_questions_are_diverse(self):
    #     """Test that generated questions are not identical"""
    #     self.authenticate_user()
    #     quiz_data = self.get_quiz_data()

    #     response = self.client.post(
    #         self.create_quiz_url, quiz_data, format='json')

    #     self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    #     self.assertEqual(len(response.data['questions']), 10)

    #     questions = response.data['questions']
    #     question_titles = [q['question_title'] for q in questions]

    #     # All question titles should be unique
    #     self.assertEqual(len(question_titles), len(set(question_titles)),
    #                      "Questions should have unique titles")

    #     # Questions should not all have the same answer
    #     answers = [q['answer'] for q in questions]
    #     unique_answers = set(answers)
    #     self.assertGreater(len(unique_answers), 1,
    #                        "Questions should have diverse answers")

    # def test_quiz_creation_with_question_generation_timing(self):
    #     """Test that question generation doesn't cause timeout"""
    #     self.authenticate_user()
    #     quiz_data = self.get_quiz_data()

    #     import time
    #     start_time = time.time()

    #     response = self.client.post(
    #         self.create_quiz_url, quiz_data, format='json')

    #     end_time = time.time()
    #     duration = end_time - start_time

    #     self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    #     self.assertEqual(len(response.data['questions']), 10)

    #     # Should complete within reasonable time (adjust as needed)
    #     self.assertLess(duration, 30, "Question generation taking too long")

    # def test_serializer_datetime_format(self):
    #     """Test that datetime fields are in correct ISO format"""
    #     self.authenticate_user()
    #     quiz_data = self.get_quiz_data()

    #     response = self.client.post(
    #         self.create_quiz_url, quiz_data, format='json')

    #     self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    #     # Check datetime format (ISO format with T and Z)
    #     created_at = response.data['created_at']
    #     updated_at = response.data['updated_at']

    #     # Should be in ISO format like "2023-07-29T12:34:56.789Z"
    #     import re
    #     datetime_pattern = r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d+Z'

    #     self.assertRegex(created_at, datetime_pattern,
    #         "created_at not in correct ISO format")
    #     self.assertRegex(updated_at, datetime_pattern,
    #         "updated_at not in correct ISO format")

    # def test_serializer_read_only_fields(self):
    #     """Test that read-only fields are not affected by input"""
    #     self.authenticate_user()
    #     quiz_data = self.get_quiz_data()

    #     # Try to set read-only fields
    #     quiz_data['id'] = 999
    #     quiz_data['created_at'] = '2020-01-01T00:00:00.000Z'
    #     quiz_data['updated_at'] = '2020-01-01T00:00:00.000Z'
    #     quiz_data['questions'] = [{'question_title': 'Should not be used'}]

    #     response = self.client.post(
    #         self.create_quiz_url, quiz_data, format='json')

    #     self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    #     # Read-only fields should be auto-generated, not from input
    #     self.assertNotEqual(response.data['id'], 999)
    #     self.assertNotEqual(
    #         response.data['created_at'], '2020-01-01T00:00:00.000Z')
    #     self.assertNotEqual(
    #         response.data['updated_at'], '2020-01-01T00:00:00.000Z')

    #     # Questions should be auto-generated (10 questions), not from input
    #     self.assertEqual(len(response.data['questions']), 10)
    #     self.assertNotEqual(
    #         response.data['questions'][0]['question_title'], 'Should not be used')

    # def test_serializer_writable_fields_only(self):
        """Test that only writable fields affect the created object"""
        self.authenticate_user()
        quiz_data = self.get_quiz_data()

        response = self.client.post(
            self.create_quiz_url, quiz_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Check that only the writable fields match input
        self.assertEqual(response.data['title'], quiz_data['title'])
        self.assertEqual(
            response.data['description'], quiz_data['description'])
        self.assertEqual(response.data['video_url'], quiz_data['video_url'])

        # Auto-generated fields should be present but not match any input
        self.assertIsNotNone(response.data['id'])
        self.assertIsNotNone(response.data['created_at'])
        self.assertIsNotNone(response.data['updated_at'])

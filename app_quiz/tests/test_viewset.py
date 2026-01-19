import warnings
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from django.urls import reverse
from django.contrib.auth import get_user_model

from ..models import Quiz, Question

User = get_user_model()


class BaseQuizViewSetTest(APITestCase):
    """Base test class for Quiz ViewSet tests"""
    
    def setUp(self):
        # Suppress warnings in tests
        warnings.filterwarnings("ignore", category=UserWarning)
        
        self.client = APIClient()
        
        # Create test users
        self.user1 = User.objects.create_user(
            username='testuser1', 
            email='test1@example.com', 
            password='testpass123'
        )
        self.user2 = User.objects.create_user(
            username='testuser2', 
            email='test2@example.com', 
            password='testpass123'
        )
        
        # Create test quiz for user1
        self.quiz1 = Quiz.objects.create(
            owner=self.user1,
            title='Python Basics Quiz',
            description='A quiz about Python programming fundamentals',
            video_url='https://www.youtube.com/watch?v=dQw4w9WgXcQ'
        )
        
        # Create test questions for quiz1
        self.question1 = Question.objects.create(
            quiz=self.quiz1,
            question_title='What is Python?',
            question_options=['Language', 'Snake', 'Tool', 'Framework'],
            answer='Language'
        )
        self.question2 = Question.objects.create(
            quiz=self.quiz1,
            question_title='What is a variable in Python?',
            question_options=['Container', 'Function', 'Class', 'Module'],
            answer='Container'
        )
        
        # Create another quiz for user1
        self.quiz2 = Quiz.objects.create(
            owner=self.user1,
            title='Django Basics Quiz',
            description='A quiz about Django framework',
            video_url='https://www.youtube.com/watch?v=example2'
        )
        
        # Create test quiz for user2
        self.quiz3 = Quiz.objects.create(
            owner=self.user2,
            title='React Basics Quiz',
            description='A quiz about React',
            video_url='https://www.youtube.com/watch?v=example3'
        )

    def authenticate_user(self, user):
        """Helper method to authenticate a specific user"""
        self.client.force_authenticate(user=user)


class QuizListTests(BaseQuizViewSetTest):
    """Tests for GET /api/quizzes/ (list all quizzes)"""
    
    def setUp(self):
        super().setUp()
        self.list_url = reverse('quiz-list')  # Adjust based on your URL name
    
    def test_list_quizzes_authenticated(self):
        """Test listing quizzes for authenticated user"""
        self.authenticate_user(self.user1)
        
        response = self.client.get(self.list_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)  # user1 has 2 quizzes
        
        # Check first quiz structure
        quiz_data = response.data[0]
        expected_fields = ['id', 'title', 'description', 'created_at', 'updated_at', 'video_url', 'questions']
        for field in expected_fields:
            self.assertIn(field, quiz_data)
        
        # Check questions are included
        self.assertIsInstance(quiz_data['questions'], list)
    
    def test_list_quizzes_unauthenticated(self):
        """Test listing quizzes without authentication"""
        response = self.client.get(self.list_url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_list_only_own_quizzes(self):
        """Test that user only sees their own quizzes"""
        self.authenticate_user(self.user2)
        
        response = self.client.get(self.list_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)  # user2 has 1 quiz
        self.assertEqual(response.data[0]['title'], 'React Basics Quiz')
    
    def test_list_empty_for_user_without_quizzes(self):
        """Test listing quizzes for user with no quizzes"""
        new_user = User.objects.create_user(
            username='newuser', 
            email='new@example.com', 
            password='pass123'
        )
        self.authenticate_user(new_user)
        
        response = self.client.get(self.list_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)


class QuizRetrieveTests(BaseQuizViewSetTest):
    """Tests for GET /api/quizzes/{id}/ (retrieve single quiz)"""
    
    def test_retrieve_own_quiz(self):
        """Test retrieving user's own quiz"""
        self.authenticate_user(self.user1)
        url = reverse('quiz-detail', kwargs={'pk': self.quiz1.pk})
        
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.quiz1.pk)
        self.assertEqual(response.data['title'], 'Python Basics Quiz')
        
        # Check all required fields are present
        expected_fields = ['id', 'title', 'description', 'created_at', 'updated_at', 'video_url', 'questions']
        for field in expected_fields:
            self.assertIn(field, response.data)
        
        # Check questions are included
        self.assertEqual(len(response.data['questions']), 2)
        
        # Check question structure
        question = response.data['questions'][0]
        question_fields = ['id', 'question_title', 'question_options', 'answer']
        for field in question_fields:
            self.assertIn(field, question)
    
    def test_retrieve_quiz_unauthenticated(self):
        """Test retrieving quiz without authentication"""
        url = reverse('quiz-detail', kwargs={'pk': self.quiz1.pk})
        
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_retrieve_other_users_quiz_returns_404(self):
        """Test that user gets 404 when accessing other user's quiz (information hiding security pattern)"""
        self.authenticate_user(self.user1)
        url = reverse('quiz-detail', kwargs={'pk': self.quiz3.pk})  # user2's quiz
        
        response = self.client.get(url)
        
        # 404 is returned because the quiz is filtered out of the queryset
        # This is a security feature that prevents quiz ID enumeration attacks
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_retrieve_nonexistent_quiz(self):
        """Test retrieving non-existent quiz"""
        self.authenticate_user(self.user1)
        url = reverse('quiz-detail', kwargs={'pk': 9999})
        
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class QuizUpdateTests(BaseQuizViewSetTest):
    """Tests for PATCH /api/quizzes/{id}/ (partial update)"""
    
    def test_partial_update_title(self):
        """Test updating only the title"""
        self.authenticate_user(self.user1)
        url = reverse('quiz-detail', kwargs={'pk': self.quiz1.pk})
        
        update_data = {'title': 'Updated Python Quiz'}
        
        response = self.client.patch(url, update_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Updated Python Quiz')
        self.assertEqual(response.data['description'], self.quiz1.description)  # Unchanged
        
        # Verify in database
        self.quiz1.refresh_from_db()
        self.assertEqual(self.quiz1.title, 'Updated Python Quiz')
    
    def test_partial_update_description(self):
        """Test updating only the description"""
        self.authenticate_user(self.user1)
        url = reverse('quiz-detail', kwargs={'pk': self.quiz1.pk})
        
        update_data = {'description': 'Updated description about Python'}
        
        response = self.client.patch(url, update_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['description'], 'Updated description about Python')
        self.assertEqual(response.data['title'], self.quiz1.title)  # Unchanged
    
    def test_partial_update_multiple_fields(self):
        """Test updating multiple fields at once"""
        self.authenticate_user(self.user1)
        url = reverse('quiz-detail', kwargs={'pk': self.quiz1.pk})
        
        update_data = {
            'title': 'New Title',
            'description': 'New Description'
        }
        
        response = self.client.patch(url, update_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'New Title')
        self.assertEqual(response.data['description'], 'New Description')
    
    def test_update_unauthenticated(self):
        """Test updating quiz without authentication"""
        url = reverse('quiz-detail', kwargs={'pk': self.quiz1.pk})
        update_data = {'title': 'Should not work'}
        
        response = self.client.patch(url, update_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_update_other_users_quiz_returns_404(self):
        """Test that user gets 404 when trying to update other user's quiz (information hiding)"""
        self.authenticate_user(self.user1)
        url = reverse('quiz-detail', kwargs={'pk': self.quiz3.pk})  # user2's quiz
        update_data = {'title': 'Hacked title'}
        
        response = self.client.patch(url, update_data, format='json')
        
        # 404 instead of 403 prevents quiz ID enumeration attacks
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_update_nonexistent_quiz(self):
        """Test updating non-existent quiz"""
        self.authenticate_user(self.user1)
        url = reverse('quiz-detail', kwargs={'pk': 9999})
        update_data = {'title': 'Does not exist'}
        
        response = self.client.patch(url, update_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_update_with_invalid_data(self):
        """Test updating with invalid data"""
        self.authenticate_user(self.user1)
        url = reverse('quiz-detail', kwargs={'pk': self.quiz1.pk})
        
        # Test with empty title
        update_data = {'title': ''}
        
        response = self.client.patch(url, update_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_update_readonly_fields_ignored(self):
        """Test that read-only fields are ignored during update"""
        self.authenticate_user(self.user1)
        url = reverse('quiz-detail', kwargs={'pk': self.quiz1.pk})
        
        original_created_at = self.quiz1.created_at
        
        update_data = {
            'title': 'New Title',
            'id': 9999,  # Should be ignored
            'created_at': '2020-01-01T00:00:00.000Z',  # Should be ignored
            'questions': []  # Should be ignored
        }
        
        response = self.client.patch(url, update_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'New Title')
        self.assertNotEqual(response.data['id'], 9999)
        self.assertNotEqual(response.data['created_at'], '2020-01-01T00:00:00.000Z')
        self.assertEqual(len(response.data['questions']), 2)  # Original questions preserved


class QuizDestroyTests(BaseQuizViewSetTest):
    """Tests for DELETE /api/quizzes/{id}/ (delete quiz)"""
    
    def test_delete_own_quiz(self):
        """Test deleting user's own quiz"""
        self.authenticate_user(self.user1)
        url = reverse('quiz-detail', kwargs={'pk': self.quiz1.pk})
        
        # Verify quiz exists before deletion
        self.assertTrue(Quiz.objects.filter(pk=self.quiz1.pk).exists())
        self.assertEqual(Question.objects.filter(quiz=self.quiz1).count(), 2)
        
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertIsNone(response.data)
        
        # Verify quiz and questions are deleted
        self.assertFalse(Quiz.objects.filter(pk=self.quiz1.pk).exists())
        self.assertEqual(Question.objects.filter(quiz=self.quiz1).count(), 0)
    
    def test_delete_unauthenticated(self):
        """Test deleting quiz without authentication"""
        url = reverse('quiz-detail', kwargs={'pk': self.quiz1.pk})
        
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        # Verify quiz still exists
        self.assertTrue(Quiz.objects.filter(pk=self.quiz1.pk).exists())
    
    def test_delete_other_users_quiz_returns_404(self):
        """Test that user gets 404 when trying to delete other user's quiz (information hiding)"""
        self.authenticate_user(self.user1)
        url = reverse('quiz-detail', kwargs={'pk': self.quiz3.pk})  # user2's quiz
        
        response = self.client.delete(url)
        
        # 404 instead of 403 prevents quiz ID enumeration attacks  
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        # Verify quiz still exists
        self.assertTrue(Quiz.objects.filter(pk=self.quiz3.pk).exists())
    
    def test_delete_nonexistent_quiz(self):
        """Test deleting non-existent quiz"""
        self.authenticate_user(self.user1)
        url = reverse('quiz-detail', kwargs={'pk': 9999})
        
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_delete_cascade_questions(self):
        """Test that deleting quiz also deletes associated questions"""
        self.authenticate_user(self.user1)
        url = reverse('quiz-detail', kwargs={'pk': self.quiz1.pk})
        
        quiz_id = self.quiz1.pk
        
        # Verify questions exist before deletion
        questions_before = Question.objects.filter(quiz_id=quiz_id).count()
        self.assertGreater(questions_before, 0)
        
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        # Verify all associated questions are deleted
        questions_after = Question.objects.filter(quiz_id=quiz_id).count()
        self.assertEqual(questions_after, 0)
    
    def test_delete_does_not_affect_other_quizzes(self):
        """Test that deleting one quiz doesn't affect other quizzes"""
        self.authenticate_user(self.user1)
        url = reverse('quiz-detail', kwargs={'pk': self.quiz1.pk})
        
        # Count quizzes before deletion
        total_quizzes_before = Quiz.objects.count()
        user1_quizzes_before = Quiz.objects.filter(owner=self.user1).count()
        
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        # Verify only one quiz was deleted
        total_quizzes_after = Quiz.objects.count()
        user1_quizzes_after = Quiz.objects.filter(owner=self.user1).count()
        
        self.assertEqual(total_quizzes_after, total_quizzes_before - 1)
        self.assertEqual(user1_quizzes_after, user1_quizzes_before - 1)
        
        # Verify other quizzes still exist
        self.assertTrue(Quiz.objects.filter(pk=self.quiz2.pk).exists())
        self.assertTrue(Quiz.objects.filter(pk=self.quiz3.pk).exists())
"""Quiz API URL patterns.

Defines URL routes for quiz management endpoints including
quiz creation from YouTube videos and CRUD operations.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import QuizViewSet, CreateQuizFromUrlView

router = DefaultRouter()
router.register(r"quizzes", QuizViewSet, basename="quiz")

urlpatterns = [
    path("createQuiz/", CreateQuizFromUrlView.as_view(), name="create_quiz_from_url"),
    path("", include(router.urls)),
]
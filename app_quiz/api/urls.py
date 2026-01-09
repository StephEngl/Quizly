from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import QuizViewSet, CreateQuizFromUrlView

router = DefaultRouter()
router.register(r"quizzes", QuizViewSet, basename="quiz")

urlpatterns = [
    path("api/createQuiz/", CreateQuizFromUrlView.as_view(), name="create_quiz_from_url"),
    path("api/", include(router.urls)),
]
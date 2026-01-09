from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets, status
from rest_framework.response import Response

from .serializers import QuizSerializer, CreateQuizFromUrlSerializer
from ..models import Quiz


class CreateQuizFromUrlView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = CreateQuizFromUrlSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        video_url = serializer.validated_data["url"]

        # 1) yt-dlp → Audio-Extraktion
        # 2) Whisper → Transkript
        # 3) Gemini → Fragen + Antworten generieren
        # 4) Quiz + Questions in DB speichern

        quiz = ...  # erstelltes Quiz-Objekt
        return Response(QuizSerializer(quiz).data, status=status.HTTP_201_CREATED)


class QuizViewSet(viewsets.ModelViewSet):
    queryset = Quiz.objects.all().prefetch_related("questions")
    serializer_class = QuizSerializer

    def create(self, request, *args, **kwargs):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
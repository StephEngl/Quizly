from drf_spectacular.utils import extend_schema, OpenApiResponse
from rest_framework import viewsets, status
from rest_framework.exceptions import MethodNotAllowed, ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from ..models import Quiz
from .permissions import IsQuizOwner
from .serializers import QuizSerializer, CreateQuizFromUrlSerializer
from .utils import normalize_youtube_url, validate_youtube_url, download_youtube_audio

@extend_schema(
    tags=['Quiz Management'],
    description="Create a quiz from a video URL.",
    responses={
        201: QuizSerializer,
        400: OpenApiResponse(description="Bad Request - Invalid URL or processing error"),
        401: OpenApiResponse(description="Unauthorized - Authentication credentials were not provided"),
    }
)
class CreateQuizFromUrlView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = CreateQuizFromUrlSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        video_url = serializer.validated_data["url"]

        try:
            # Normalize YouTube URL to standard format
            normalized_url = normalize_youtube_url(video_url)
            
            # Download audio file and get video title
            audio_file_path, video_title = download_youtube_audio(normalized_url)
            
            # For testing: return info about the downloaded audio
            return Response({
                "message": "Audio successfully downloaded",
                "video_title": video_title,
                "audio_file": audio_file_path,
                "normalized_url": normalized_url
            }, status=status.HTTP_200_OK)
            
        except ValueError as e:
            raise ValidationError({"url": f"Invalid YouTube URL: {str(e)}"})
        except RuntimeError as e:
            raise ValidationError({"url": f"Audio download failed: {str(e)}"})

        # TODO: Next steps after successful audio download:
        # 1) Whisper → Transkript aus audio_file_path
        # 2) Gemini → Fragen + Antworten generieren
        # 3) Quiz + Questions in DB speichern
        # 4) Cleanup: os.remove(audio_file_path)

        # quiz = ...  # erstelltes Quiz-Objekt
        # return Response(QuizSerializer(quiz).data, status=status.HTTP_201_CREATED)


@extend_schema(
    tags=['Quiz Management'],
    description="Manage quizzes created by users.",
)
class QuizViewSet(viewsets.ModelViewSet):
    queryset = Quiz.objects.all().prefetch_related("questions")
    serializer_class = QuizSerializer
    permission_classes = [IsAuthenticated, IsQuizOwner]
    http_method_names = ['get', 'patch', 'delete', 'head', 'options']

    @extend_schema(exclude=True)
    def create(self, request, *args, **kwargs):
        """
        Disable CREATE detail endpoint.
        """
        return MethodNotAllowed("CREATE")
    
    @extend_schema(
        responses={
            200: QuizSerializer(many=True),
            401: OpenApiResponse(description="User is unauthorized"),
        }
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    @extend_schema(exclude=True)
    def update(self, request, *args, **kwargs):
        """
        Disable UPDATE detail endpoint.
        """
        return MethodNotAllowed("UPDATE")
    
    @extend_schema(
        responses={
            200: QuizSerializer,
            400: OpenApiResponse(description="Bad Request"),
            401: OpenApiResponse(description="User is unauthorized"),
            403: OpenApiResponse(description="User is not the quiz owner"),
            404: OpenApiResponse(description="Quiz not Found"),
        }
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @extend_schema(
        responses={
            204: OpenApiResponse(description="Quiz deleted successfully"),
            401: OpenApiResponse(description="User is unauthorized"),
            403: OpenApiResponse(description="User is not the quiz owner"),
            404: OpenApiResponse(description="Quiz not Found"),
        }
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)
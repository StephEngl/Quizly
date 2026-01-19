from drf_spectacular.utils import extend_schema, OpenApiResponse
from rest_framework import viewsets, status
from rest_framework.exceptions import MethodNotAllowed, ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from app_auth.api.views import CookieJWTAuthentication
from ..models import Quiz, Question
from .permissions import IsQuizOwner
from .serializers import QuizSerializer, CreateQuizFromUrlSerializer, CreateQuizSerializer
from .utils import download_and_transcribe, generate_quiz_from_transcript

@extend_schema(
    tags=['Quiz Management'],
    description="Create a quiz from a youtube video URL.",
    responses={
        201: QuizSerializer,
        400: OpenApiResponse(description="Bad Request - Invalid URL or processing error"),
        401: OpenApiResponse(description="Unauthorized - Authentication credentials were not provided"),
    }
)
class CreateQuizFromUrlView(APIView):
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = CreateQuizFromUrlSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        video_url = serializer.validated_data["url"]

        try:
            # Download audio and transcribe with Whisper (yt-dlp handles URL normalization)
            transcript, video_title = download_and_transcribe(video_url)
            
            # 2) Generate quiz from transcript using Gemini
            quiz_data = generate_quiz_from_transcript(transcript)
            
            # 3) Create Quiz in database
            quiz = Quiz.objects.create(
                owner=request.user,
                title=quiz_data["title"],
                description=quiz_data["description"],
                video_url=video_url
            )
            
            # 4) Create Questions in database
            for question_data in quiz_data["questions"]:
                Question.objects.create(
                    quiz=quiz,
                    question_title=question_data["question_title"],
                    question_options=question_data["question_options"],
                    answer=question_data["answer"]
                )
            
            # 5) Return complete quiz with questions
            return Response(CreateQuizSerializer(quiz).data, status=status.HTTP_201_CREATED)
            
        except RuntimeError as error:
            raise ValidationError({"error": f"Processing failed: {str(error)}"})


@extend_schema(
    tags=['Quiz Management'],
    description="Manage quizzes created by users.",
)
class QuizViewSet(viewsets.ModelViewSet):
    serializer_class = QuizSerializer
    permission_classes = [IsAuthenticated, IsQuizOwner]
    authentication_classes = [CookieJWTAuthentication]
    http_method_names = ['get', 'patch', 'delete', 'head', 'options']

    def get_queryset(self):
        """Only return quizzes owned by the current user"""
        return Quiz.objects.filter(owner=self.request.user).prefetch_related("questions")

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
    
    @extend_schema(
        responses={
            200: QuizSerializer,
            401: OpenApiResponse(description="User is unauthorized"),
            403: OpenApiResponse(description="User is not the quiz owner"),
            404: OpenApiResponse(description="Quiz not Found"),
        }
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
    
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
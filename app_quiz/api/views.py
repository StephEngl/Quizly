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
from .utils import download_and_transcribe, check_for_duplicate_quiz, create_quiz_from_transcript

@extend_schema(
    tags=['Quiz Management'],
    description="Create a quiz from a youtube video URL.",
    responses={
        201: CreateQuizSerializer,
        400: OpenApiResponse(description="Bad Request - Invalid URL or processing error"),
        401: OpenApiResponse(description="Unauthorized - Authentication credentials were not provided"),
    }
)
class CreateQuizFromUrlView(APIView):
    """API view to create a quiz from a YouTube video URL.
    
    Downloads video audio, transcribes it, checks for duplicates,
    and generates quiz using Gemini AI.
    """
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        """Create a new quiz from YouTube video URL.
            
        Returns:
            Response: Created quiz data or validation error.
            
        Raises:
            ValidationError: If URL invalid or processing fails.
        """
        serializer = CreateQuizFromUrlSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        video_url = serializer.validated_data["url"]

        try:
            transcript, video_title = download_and_transcribe(video_url)
            check_for_duplicate_quiz(request.user, video_url, video_title)
            quiz = create_quiz_from_transcript(request.user, transcript, video_url)
            
            return Response(CreateQuizSerializer(quiz).data, status=status.HTTP_201_CREATED)
            
        except RuntimeError as error:
            raise ValidationError({"error": f"Processing failed: {str(error)}"})


@extend_schema(
    tags=['Quiz Management'],
    description="Manage quizzes created by users.",
)
class QuizViewSet(viewsets.ModelViewSet):
    """ViewSet for managing user's quiz collection.
    
    Provides CRUD operations for quizzes. Users can only
    access their own quizzes.
    """
    serializer_class = QuizSerializer
    permission_classes = [IsAuthenticated, IsQuizOwner]
    authentication_classes = [CookieJWTAuthentication]
    http_method_names = ['get', 'patch', 'delete', 'head', 'options']

    def get_queryset(self):
        """Return quizzes owned by the authenticated user.
        
        Returns:
            QuerySet: User's quizzes with prefetched questions.
        """
        return Quiz.objects.filter(owner=self.request.user).prefetch_related("questions")

    @extend_schema(exclude=True)
    def create(self, request, *args, **kwargs):
        """Disable quiz creation via this endpoint.
        
        Raises:
            MethodNotAllowed: Always, as creation is disabled.
        """
        return MethodNotAllowed("CREATE")
    
    @extend_schema(
        responses={
            200: QuizSerializer(many=True),
            401: OpenApiResponse(description="User is unauthorized"),
        }
    )
    def list(self, request, *args, **kwargs):
        """List all quizzes owned by the user."""
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
        """Retrieve a specific quiz by ID."""
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
        """Partially update a quiz."""
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
        """Delete a quiz permanently."""
        return super().destroy(request, *args, **kwargs)
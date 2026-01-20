from rest_framework import serializers
from ..models import Quiz, Question


class QuestionSerializer(serializers.ModelSerializer):
    """Serializer for quiz questions.
    
    Serializes question data including title, options, and correct answer
    for API responses when retrieving quiz information.
    """
    question_options = serializers.ListField(
        child=serializers.CharField(), 
        help_text="List of answer options for the question"
    )
    
    class Meta:
        model = Question
        fields = ['id', 'question_title', 'question_options', 'answer']


class QuizSerializer(serializers.ModelSerializer):
    """Serializer for quiz data with nested questions.
    
    Includes all quiz information along with associated questions
    for complete quiz representation in API responses.
    """
    questions = QuestionSerializer(many=True, read_only=True)
    
    class Meta:
        model = Quiz
        fields = ['id', 'title', 'description', 'created_at', 'updated_at', 'video_url', 'questions']


class CreateQuizQuestionSerializer(serializers.ModelSerializer):
    """Serializer for questions in quiz creation responses.
    
    Extended question serializer that includes timestamp information
    for newly created quiz questions.
    """
    question_options = serializers.ListField(
        child=serializers.CharField(), 
        help_text="List of answer options for the question"
    )
    
    class Meta:
        model = Question
        fields = ['id', 'question_title', 'question_options', 'answer', 'created_at', 'updated_at']


class CreateQuizSerializer(serializers.ModelSerializer):
    """Serializer for quiz creation responses.
    
    Returns complete quiz data including timestamps and nested questions
    after successful quiz creation from YouTube video.
    """
    questions = CreateQuizQuestionSerializer(many=True, read_only=True)
    
    class Meta:
        model = Quiz
        fields = ['id', 'title', 'description', 'created_at', 'updated_at', 'video_url', 'questions']


class CreateQuizFromUrlSerializer(serializers.Serializer):
    """Serializer for quiz creation from YouTube URL.
    
    Validates YouTube URL input for the quiz creation endpoint
    that processes video content into quiz questions.
    """
    url = serializers.URLField(help_text="YouTube URL to create quiz from")
import os
import re
import json
import yt_dlp
import whisper
from google import genai
from django.db import transaction
from rest_framework.exceptions import ValidationError

from ..models import Quiz, Question


# yt-dlp configuration for audio download
YT_DLP_OPTIONS = {
    'format': 'm4a/bestaudio/best',
    'quiet': True,
    'noplaylist': True,
    'http_headers': {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept-Language': 'en-US,en;q=0.8',
        'Accept': '*/*',
        'Referer': 'https://www.youtube.com/',
        'Origin': 'https://www.youtube.com'
    },
}

# Gemini AI prompt template for quiz generation
QUIZ_GENERATION_PROMPT = """Based on the following transcript, generate a quiz in valid JSON format.

The quiz must follow this exact structure:

{
    "title": "Create a concise quiz title based on the topic of the transcript.",
    "description": "Summarize the transcript in no more than 150 characters. Do not include any quiz questions or answers.",
    "questions": [
        {
        "question_title": "The question goes here.",
        "question_options": ["Option A", "Option B", "Option C", "Option D"],
        "answer": "The correct answer from the above options"
        },
        ...
        (exactly 10 questions)
    ]
}

Requirements:
- Each question must have exactly 4 distinct answer options.
- Only one correct answer is allowed per question, and it must be present in 'question_options'.
- The output must be valid JSON and parsable as-is (e.g., using Python's json.loads).
- Do not include explanations, comments, or any text outside the JSON."""


def download_and_transcribe(url, media_root="media"):
    """Download YouTube video audio and transcribe to text using Whisper."""
    os.makedirs(media_root, exist_ok=True)

    ydl_opts = YT_DLP_OPTIONS.copy()
    ydl_opts['outtmpl'] = os.path.join(media_root, '%(id)s.%(ext)s')

    audio_filename = None
    transcript = ""
    video_title = ""

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            audio_filename = ydl.prepare_filename(info)
            video_title = info.get("title", "Untitled Video")

            model = whisper.load_model("tiny")
            result = model.transcribe(audio_filename)
            transcript = result["text"].strip()

    except yt_dlp.DownloadError as error:
        raise RuntimeError(f"yt-dlp download failed: {str(error)}")
    except Exception as error:
        raise RuntimeError(f"Unexpected error: {str(error)}")
    finally:
        if audio_filename and os.path.exists(audio_filename):
            os.remove(audio_filename)

    return transcript, video_title


def extract_json_from_response(response_text):
    """Clean and parse JSON from Gemini API response text."""
    cleaned_json = re.sub(r"^```(?:json)?|```$", "", response_text, flags=re.DOTALL).strip()
    return json.loads(cleaned_json)


def generate_quiz_from_transcript(transcript):
    """Generate quiz data from transcript using Gemini AI."""
    try:
        client = genai.Client()

        response = client.models.generate_content(
            model="gemini-2.5-flash-lite",
            contents=[QUIZ_GENERATION_PROMPT, transcript]
        )

        response_text = response.candidates[0].content.parts[0].text
        quiz_data = extract_json_from_response(response_text)
        return quiz_data

    except Exception as error:
        raise RuntimeError(f"Gemini API failed: {str(error)}")


def check_for_duplicate_quiz(user, video_url, video_title):
    """Check if user already has a quiz from this video."""
    existing_quiz = Quiz.objects.filter(
        owner=user,
        video_url=video_url
    ).first()
    
    if existing_quiz:
        raise ValidationError({
            "error": f"You already have a quiz from this video: '{video_title}'"
        })


@transaction.atomic
def create_quiz_from_transcript(user, transcript, video_url):
    """Generate and create quiz with questions atomically."""
    quiz_data = generate_quiz_from_transcript(transcript)
    
    quiz = Quiz.objects.create(
        owner=user,
        title=quiz_data["title"],
        description=quiz_data["description"],
        video_url=video_url
    )
    
    create_questions_for_quiz(quiz, quiz_data["questions"])
    
    return quiz


def create_questions_for_quiz(quiz, questions_data):
    """Create Question objects for the given quiz."""
    for question_data in questions_data:
        Question.objects.create(
            quiz=quiz,
            question_title=question_data["question_title"],
            question_options=question_data["question_options"],
            answer=question_data["answer"]
        )
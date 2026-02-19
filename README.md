<div style="display: flex; align-items: center;">
  <img src="assets/logo.png" alt="Quizly Logo" style="height: 60px; margin-right: 16px;">
  <h1 style="margin: 0;">Quizly Django Project</h1>
</div>
<div style="height:16px"></div>
Quizly provides an intelligent quiz generation platform that transforms YouTube videos into interactive learning experiences. Built with Python and powered by AI, Quizly offers an innovative solution for creating educational content from video transcripts. Key features include AI-powered quiz generation using Gemini AI, secure user authentication, comprehensive quiz management, and a robust REST API for seamless integration.

## ✨ Features

🎥 **YouTube Video Processing** - Extract audio and transcribe content from YouTube videos  
🤖 **AI Quiz Generation** - Generate intelligent quiz questions using Gemini AI  
🔐 **Authentication** - Secure user registration, login, and JWT token management  
📚 **Quiz Management** - Create, read, update, and delete personal quizzes  
🛡️ **User Permissions** - Users can only access and manage their own quizzes  
🧪 **Testing** - Comprehensive test suite ensuring reliability and stability

## 🛠️ Tech Stack

- **Python** - Core programming language
- **Django** - Web framework
- **Django REST Framework** - API development
- **Gemini AI** - Quiz question generation
- **Whisper** - Audio transcription
- **yt-dlp** - YouTube video processing
- **SQLite** - Database (development)

## 🚀 Getting Started

Follow these steps to set up and run the project locally.

### ⚙️ Prerequisites

- Python 3.10+
- pip (Python package manager)
- Virtualenv (recommended)
- Gemini AI API key

### 📦 Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/StephEngl/Quizly.git
   cd Quizly
   ```

2. **Create and activate a virtual environment**
   ```bash
   python -m venv env
   env\Scripts\activate  # On Mac: source env/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   Copy the .env.template to .env and replace the placeholder values with your API keys:
   ``` bash
   cp .env.template .env
   ```
   ```
   GEMINI_API_KEY=your_gemini_api_key_here
   SECRET_KEY=your_django_secret_key_here
   ```

5. **Apply migrations**
   ```bash
   python manage.py migrate
   ```

6. **Create a superuser (optional, for admin access)**
   ```bash
   python manage.py createsuperuser
   ```

7. **Run the development server**
   ```bash
   python manage.py runserver
   ```

## 📚 API Documentation

This project includes automatically generated API documentation with Swagger UI and Redoc.

**The OpenAPI schema is available at:**
- `/api/schema/`

**Interactive Swagger UI can be accessed at:**
- `/api/schema/swagger-ui/`  
  Use this web interface to explore and test the API endpoints easily.

**Alternative documentation with Redoc is available at:**
- `/api/schema/redoc/`

These endpoints are integrated using drf-spectacular and configured in the Django URL patterns for convenient API exploration during development and testing.

## 📁 Project Structure

- [`core`](core) – Project configuration, global settings, and root URLs
- [`app_auth`](app_auth) – Handles user authentication, registration, and JWT token management
- [`app_quiz`](app_quiz) – Manages quiz creation from YouTube videos, CRUD operations, and AI generation
- [`media`](media) – Stores temporary audio files during processing

## 🔗 API Endpoints

### 🛡️ Authentication
- `POST /api/register/` – Register new user account
- `POST /api/login/` – User login and token generation
- `POST /api/token/refresh/` – Refresh JWT access token
- `POST /api/logout/` – User logout and token cleanup

### 📝 Quiz Management
- `POST /api/createQuiz/` – Create quiz from YouTube video URL
- `GET /api/quizzes/` – List all user's quizzes
- `GET /api/quizzes/{id}/` – Retrieve specific quiz with questions
- `PATCH /api/quizzes/{id}/` – Partially update quiz information
- `DELETE /api/quizzes/{id}/` – Delete quiz permanently

## 🎯 How It Works

1. **Video Processing**: User provides a YouTube URL
2. **Audio Extraction**: System downloads and extracts audio using yt-dlp
3. **Transcription**: Audio is transcribed to text using Whisper AI
4. **Quiz Generation**: Gemini AI processes transcript and generates 10 multiple-choice questions
5. **Storage**: Quiz and questions are saved to the database
6. **Access**: Users can view, edit, and manage their generated quizzes

## 🔒 Security Information

- **Secret Key**: Never share your Django SECRET_KEY. Use environment variables for production.
- **Debug Mode**: Set `DEBUG = False` in production.
- **Allowed Hosts**: Update `ALLOWED_HOSTS` in settings.py for your deployment.
- **API Keys**: Store Gemini AI API keys in environment variables, not in code.
- **Database**: Use strong credentials and restrict access in production.
- **HTTPS**: Always use HTTPS in production.
- **Admin Panel**: Restrict admin access and use strong passwords.
- **.env Files**: Make sure .env files are not pushed to the repo (see .gitignore).
- **Database Files**: Do not commit database files (*.sqlite3).

## 🧪 Running Tests

Run the comprehensive test suite to ensure everything works correctly:

```bash
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test app_quiz
python manage.py test app_auth

# Run with coverage analysis
coverage run --source='.' manage.py test
coverage report
```

## 👥 Contributing

Contributions are welcome! Here's how you can help:

1. Fork the repository
2. Clone your fork: `git clone https://github.com/StephEngl/Quizly.git`
3. Create a new branch: `git checkout -b feature/your-feature`
4. Commit your changes: `git commit -am 'Add some feature'`
5. Push to your branch: `git push origin feature/your-feature`
6. Open a pull request

Please ensure your code follows the project's style guidelines and includes tests where applicable.

## 🔧 Configuration

For more details about project configuration, see:
- [core/settings.py](core/settings.py) - Django settings and configurations
- [core/urls.py](core/urls.py) - URL routing and API endpoint definitions
- [requirements.txt](requirements.txt) - Python dependencies

## 📄 License

This project is licensed under the MIT License. See the LICENSE file for details.

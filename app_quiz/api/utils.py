import os
import yt_dlp
import whisper


def download_and_transcribe(url, media_root="media"):
    """
    Download audio from a YouTube video and transcribe it to text.

    This function:
    - Downloads the audio from the provided YouTube URL as VIDEO_ID.m4a/mp3/webm
    - Uses the Whisper 'tiny' model to transcribe the audio into text
    - Deletes the audio file after transcription
    - Returns both transcript and video title

    Args:
        url (str): The URL of the YouTube video
        media_root (str): Directory to save temporary audio files (default: "media")

    Returns:
        tuple: (transcript_text, video_title)

    Raises:
        yt_dlp.utils.DownloadError: If the video cannot be downloaded
        RuntimeError: If transcription fails
    """
    
    # Create media folder if not existing
    os.makedirs(media_root, exist_ok=True)
    
    # yt-dlp options - elegant and automatic
    ydl_opts = {
        'format': 'm4a/bestaudio/best',  # Try m4a first, fallback to best audio
        "quiet": True,
        "noplaylist": True,
        'outtmpl': os.path.join(media_root, '%(id)s.%(ext)s'),  # Save as VIDEO_ID.ext
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept-Language': 'en-US,en;q=0.8',
            'Accept': '*/*',
            'Referer': 'https://www.youtube.com/',
            'Origin': 'https://www.youtube.com'
        },
    }
    
    audio_filename = None
    transcript = ""
    video_title = ""
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Extract info and download in one step
            info = ydl.extract_info(url, download=True)  # yt-dlp handles URL normalization!
            
            # Get the exact filename that yt-dlp created
            audio_filename = ydl.prepare_filename(info)
            
            # Get video title from info
            video_title = info.get("title", "Untitled Video")
            
            # Load Whisper model and transcribe
            model = whisper.load_model("tiny")
            result = model.transcribe(audio_filename)
            transcript = result["text"].strip()

    except yt_dlp.DownloadError as error:
        raise RuntimeError(f"yt-dlp download failed: {str(error)}")
    except Exception as error:
        raise RuntimeError(f"Unexpected error: {str(error)}")
    finally:
        # Always cleanup audio file after transcription
        if audio_filename and os.path.exists(audio_filename):
            os.remove(audio_filename)
    
    return transcript, video_title
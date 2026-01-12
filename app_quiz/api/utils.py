import os
import re
import tempfile
import uuid
from pathlib import Path
from urllib.parse import urlparse, parse_qs

import yt_dlp


def normalize_youtube_url(url):
    """
    Normalizes YouTube URLs to the standard format: https://www.youtube.com/watch?v=VIDEO_ID
    
    Supports formats:
    - https://www.youtube.com/watch?v=TxHM390wrRk
    - https://youtu.be/TxHM390wrRk
    - https://youtu.be/TxHM390wrRk?si=MQFw2eEIvF4LeD3S
    - https://youtube.com/watch?v=TxHM390wrRk
    - https://m.youtube.com/watch?v=TxHM390wrRk
    
    Args:
        url (str): The YouTube URL to normalize
        
    Returns:
        str: Normalized YouTube URL in format https://www.youtube.com/watch?v=VIDEO_ID
        
    Raises:
        ValueError: If the URL is not a valid YouTube URL or video ID cannot be extracted
    """
    if not url or not isinstance(url, str):
        raise ValueError("URL must be a non-empty string")
    
    # Remove any whitespace
    url = url.strip()
    
    # Extract video ID using regex patterns
    video_id = None
    
    # Pattern 1: youtu.be/VIDEO_ID (short format)
    short_pattern = r'(?:https?://)?(?:www\.)?youtu\.be/([a-zA-Z0-9_-]{11})'
    match = re.search(short_pattern, url)
    if match:
        video_id = match.group(1)
    
    # Pattern 2: youtube.com/watch?v=VIDEO_ID (standard format)
    if not video_id:
        long_pattern = r'(?:https?://)?(?:www\.|m\.)?youtube\.com/watch\?.*v=([a-zA-Z0-9_-]{11})'
        match = re.search(long_pattern, url)
        if match:
            video_id = match.group(1)
    
    # Pattern 3: Try to extract from URL parameters
    if not video_id:
        try:
            parsed_url = urlparse(url)
            if 'youtube.com' in parsed_url.netloc:
                query_params = parse_qs(parsed_url.query)
                if 'v' in query_params:
                    potential_id = query_params['v'][0]
                    if len(potential_id) == 11:
                        video_id = potential_id
        except:
            pass
    
    if not video_id:
        raise ValueError(f"Could not extract video ID from URL: {url}")
    
    # Validate video ID format (YouTube video IDs are 11 characters)
    if not re.match(r'^[a-zA-Z0-9_-]{11}$', video_id):
        raise ValueError(f"Invalid YouTube video ID format: {video_id}")
    
    return f"https://www.youtube.com/watch?v={video_id}"


def extract_video_id(url):
    """
    Extracts just the video ID from a YouTube URL
    
    Args:
        url (str): The YouTube URL
        
    Returns:
        str: The 11-character video ID
        
    Raises:
        ValueError: If video ID cannot be extracted
    """
    normalized_url = normalize_youtube_url(url)
    return normalized_url.split('v=')[1]


def validate_youtube_url(url):
    """
    Validates if a URL is a valid YouTube URL
    
    Args:
        url (str): The URL to validate
        
    Returns:
        bool: True if valid YouTube URL, False otherwise
    """
    try:
        normalize_youtube_url(url)
        return True
    except ValueError:
        return False


def download_youtube_audio(url, output_dir=None):
    """
    Downloads audio from a YouTube video using yt-dlp
    
    Args:
        url (str): The YouTube URL to download audio from
        output_dir (str, optional): Directory to save the audio file. 
                                If None, uses system temp directory.
    
    Returns:
        tuple: (audio_file_path, video_title)
        
    Raises:
        ValueError: If the URL is invalid or download fails
        RuntimeError: If yt-dlp fails to download the audio
    """
    # Normalize the URL first
    normalized_url = normalize_youtube_url(url)
    
    # Create output directory if not specified
    if output_dir is None:
        output_dir = tempfile.gettempdir()
    else:
        Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    # Generate unique filename to avoid conflicts
    unique_id = str(uuid.uuid4())[:8]
    tmp_filename = os.path.join(output_dir, f"audio_{unique_id}.%(ext)s")
    
    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": tmp_filename,
        "quiet": True,
        "noplaylist": True,
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Extract info first to get the title and download
            info = ydl.extract_info(normalized_url, download=False)
            if not info:
                raise RuntimeError("Could not extract video information")
            
            video_title = info.get("title", "Untitled Video")
            
            # Download the audio
            ydl.download([normalized_url])
            
            # Find the downloaded file
            # yt-dlp replaces %(ext)s with the actual extension
            base_filename = tmp_filename.replace(".%(ext)s", "")
            for ext in ['.webm', '.m4a', '.mp3', '.wav', '.ogg']:
                potential_file = f"{base_filename}{ext}"
                if os.path.exists(potential_file):
                    return potential_file, video_title
            
            raise RuntimeError("Downloaded audio file not found")
            
    except yt_dlp.DownloadError as e:
        raise RuntimeError(f"yt-dlp download failed: {str(e)}")
    except Exception as e:
        raise RuntimeError(f"Unexpected error during audio download: {str(e)}")
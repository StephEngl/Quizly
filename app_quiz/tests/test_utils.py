import unittest
from ..api.utils import normalize_youtube_url, extract_video_id, validate_youtube_url


class TestYouTubeUtils(unittest.TestCase):
    """Test cases for YouTube URL utility functions"""

    def test_normalize_youtube_url_standard_format(self):
        """Test with standard YouTube URL format"""
        url = "https://www.youtube.com/watch?v=TxHM390wrRk"
        expected = "https://www.youtube.com/watch?v=TxHM390wrRk"
        result = normalize_youtube_url(url)
        self.assertEqual(result, expected)

    def test_normalize_youtube_url_short_format(self):
        """Test with short YouTube URL format (youtu.be)"""
        url = "https://youtu.be/TxHM390wrRk"
        expected = "https://www.youtube.com/watch?v=TxHM390wrRk"
        result = normalize_youtube_url(url)
        self.assertEqual(result, expected)

    def test_normalize_youtube_url_with_parameters(self):
        """Test with YouTube URL containing additional parameters"""
        url = "https://youtu.be/TxHM390wrRk?si=MQFw2eEIvF4LeD3S"
        expected = "https://www.youtube.com/watch?v=TxHM390wrRk"
        result = normalize_youtube_url(url)
        self.assertEqual(result, expected)

    def test_normalize_youtube_url_without_protocol(self):
        """Test with YouTube URL without https://"""
        url = "www.youtube.com/watch?v=TxHM390wrRk"
        expected = "https://www.youtube.com/watch?v=TxHM390wrRk"
        result = normalize_youtube_url(url)
        self.assertEqual(result, expected)

    def test_normalize_youtube_url_mobile(self):
        """Test with mobile YouTube URL"""
        url = "https://m.youtube.com/watch?v=TxHM390wrRk"
        expected = "https://www.youtube.com/watch?v=TxHM390wrRk"
        result = normalize_youtube_url(url)
        self.assertEqual(result, expected)

    def test_normalize_youtube_url_with_additional_params(self):
        """Test with YouTube URL containing multiple parameters"""
        url = "https://www.youtube.com/watch?v=TxHM390wrRk&t=123s&list=PLxxx"
        expected = "https://www.youtube.com/watch?v=TxHM390wrRk"
        result = normalize_youtube_url(url)
        self.assertEqual(result, expected)

    def test_normalize_youtube_url_invalid_url(self):
        """Test with invalid URL"""
        url = "https://www.example.com/watch?v=TxHM390wrRk"
        with self.assertRaises(ValueError):
            normalize_youtube_url(url)

    def test_normalize_youtube_url_empty_string(self):
        """Test with empty string"""
        with self.assertRaises(ValueError):
            normalize_youtube_url("")

    def test_normalize_youtube_url_none(self):
        """Test with None"""
        with self.assertRaises(ValueError):
            normalize_youtube_url(None)

    def test_extract_video_id(self):
        """Test video ID extraction"""
        url = "https://youtu.be/TxHM390wrRk?si=MQFw2eEIvF4LeD3S"
        expected = "TxHM390wrRk"
        result = extract_video_id(url)
        self.assertEqual(result, expected)

    def test_validate_youtube_url_valid(self):
        """Test URL validation with valid YouTube URL"""
        url = "https://youtu.be/TxHM390wrRk"
        self.assertTrue(validate_youtube_url(url))

    def test_validate_youtube_url_invalid(self):
        """Test URL validation with invalid URL"""
        url = "https://www.example.com/video"
        self.assertFalse(validate_youtube_url(url))

    def test_normalize_youtube_url_invalid_video_id_length(self):
        """Test with invalid video ID length"""
        url = "https://www.youtube.com/watch?v=short"
        with self.assertRaises(ValueError):
            normalize_youtube_url(url)
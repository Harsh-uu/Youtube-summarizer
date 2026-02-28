"""
extract_video_id.py
-------------------
Extracts the YouTube video ID from various URL formats:
  - https://www.youtube.com/watch?v=VIDEO_ID
  - https://www.youtube.com/watch?v=VIDEO_ID&t=120
  - https://youtu.be/VIDEO_ID
  - https://youtu.be/VIDEO_ID?t=120
  - https://youtube.com/shorts/VIDEO_ID
  - https://youtube.com/embed/VIDEO_ID
  - Plain video ID string (11 characters)

Returns the video ID string, or raises ValueError if the URL is invalid.
"""

import re


# Regex patterns for supported YouTube URL formats
YOUTUBE_PATTERNS = [
    # Standard watch URL: youtube.com/watch?v=ID (may have extra params)
    r'(?:https?://)?(?:www\.)?youtube\.com/watch\?.*v=([a-zA-Z0-9_-]{11})',
    # Short URL: youtu.be/ID (may have ?t=... or ?si=...)
    r'(?:https?://)?youtu\.be/([a-zA-Z0-9_-]{11})',
    # Shorts URL: youtube.com/shorts/ID
    r'(?:https?://)?(?:www\.)?youtube\.com/shorts/([a-zA-Z0-9_-]{11})',
    # Embed URL: youtube.com/embed/ID
    r'(?:https?://)?(?:www\.)?youtube\.com/embed/([a-zA-Z0-9_-]{11})',
    # Live URL: youtube.com/live/ID
    r'(?:https?://)?(?:www\.)?youtube\.com/live/([a-zA-Z0-9_-]{11})',
]

# A bare video ID is exactly 11 alphanumeric / dash / underscore characters
BARE_ID_PATTERN = r'^[a-zA-Z0-9_-]{11}$'


def extract_video_id(url_or_id: str) -> str:
    """
    Extract a YouTube video ID from a URL string or bare ID.

    Args:
        url_or_id: A YouTube URL or an 11-character video ID.

    Returns:
        The 11-character video ID.

    Raises:
        ValueError: If the input doesn't match any known YouTube URL format.
    """
    text = url_or_id.strip()

    # Check if it's already a bare video ID
    if re.match(BARE_ID_PATTERN, text):
        return text

    # Try each URL pattern
    for pattern in YOUTUBE_PATTERNS:
        match = re.search(pattern, text)
        if match:
            return match.group(1)

    raise ValueError(
        f"Could not extract a YouTube video ID from: {text}\n"
        "Supported formats:\n"
        "  - https://www.youtube.com/watch?v=VIDEO_ID\n"
        "  - https://youtu.be/VIDEO_ID\n"
        "  - https://youtube.com/shorts/VIDEO_ID\n"
        "  - A plain 11-character video ID"
    )

"""
format_transcript.py
--------------------
Converts the raw transcript data (list of dicts from youtube-transcript-api)
into a clean, readable string with timestamps.

Each segment becomes:
  [MM:SS] Text of the segment...
"""


def seconds_to_timestamp(seconds: float) -> str:
    """Convert seconds (float) to MM:SS or HH:MM:SS format."""
    total = int(seconds)
    hrs = total // 3600
    mins = (total % 3600) // 60
    secs = total % 60

    if hrs > 0:
        return f"{hrs:02d}:{mins:02d}:{secs:02d}"
    return f"{mins:02d}:{secs:02d}"


def format_transcript(transcript_segments: list) -> str:
    """
    Format raw transcript segments into readable timestamped text.

    Args:
        transcript_segments: List of dicts, each with keys:
            - 'text': the caption text
            - 'start': start time in seconds
            - 'duration': duration in seconds

    Returns:
        A single string with one line per segment:
            [00:00] First line of captions
            [00:05] Second line of captions
            ...
    """
    if not transcript_segments:
        return ""

    lines = []
    for segment in transcript_segments:
        timestamp = seconds_to_timestamp(segment["start"])
        text = segment["text"].strip()
        if text:  # skip empty segments
            lines.append(f"[{timestamp}] {text}")

    return "\n".join(lines)

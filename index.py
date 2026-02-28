"""
index.py — YouTube Transcript Fetcher
--------------------------------------
Main entry point for the YouTube Summarizer skill.

Usage:
    python index.py <video_id_or_url>

Fetches the transcript for the given YouTube video and prints it
as formatted, timestamped text to stdout. OpenClaw captures this
output and passes it to the LLM for summarization / Q&A.

Features:
    - Supports all YouTube URL formats (watch, youtu.be, shorts, embed, live)
    - Tries English first, falls back to any available language
    - Caches transcripts locally to avoid redundant API calls
    - Chunks long transcripts for LLM context limits
    - Comprehensive error handling with user-friendly messages

Exit codes:
    0 — success
    1 — error (message printed to stderr)
"""

import sys
import json
import io
import os
import time

# Force UTF-8 output on Windows to handle Unicode characters in transcripts
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

from youtube_transcript_api import (
    YouTubeTranscriptApi,
    NoTranscriptFound,
    TranscriptsDisabled,
    VideoUnavailable,
    InvalidVideoId,
    RequestBlocked,
    IpBlocked,
)

from utils.extract_video_id import extract_video_id
from utils.format_transcript import format_transcript
from utils.chunk_transcript import chunk_transcript

# --- Cache config ---
# Cache directory lives inside the skill folder
CACHE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cache")
CACHE_TTL_SECONDS = 7 * 24 * 3600  # 7 days


def get_cached_transcript(video_id: str) -> list | None:
    """
    Check if a cached transcript exists for this video ID.

    Returns:
        List of transcript segment dicts if cached and not expired, else None.
    """
    cache_file = os.path.join(CACHE_DIR, f"{video_id}.json")
    if not os.path.exists(cache_file):
        return None

    try:
        with open(cache_file, "r", encoding="utf-8") as f:
            cached = json.load(f)

        # Check if cache has expired
        cached_at = cached.get("cached_at", 0)
        if time.time() - cached_at > CACHE_TTL_SECONDS:
            os.remove(cache_file)
            return None

        return cached.get("segments", None)
    except (json.JSONDecodeError, OSError):
        return None


def save_to_cache(video_id: str, segments: list) -> None:
    """Save transcript segments to the local cache."""
    os.makedirs(CACHE_DIR, exist_ok=True)
    cache_file = os.path.join(CACHE_DIR, f"{video_id}.json")
    try:
        with open(cache_file, "w", encoding="utf-8") as f:
            json.dump({"video_id": video_id, "cached_at": time.time(), "segments": segments}, f)
    except OSError:
        pass  # Cache write failure is non-critical


def fetch_transcript(video_id: str) -> list:
    """
    Fetch the transcript for a YouTube video using youtube-transcript-api v1.x.

    Strategy:
      1. Try English transcript first
      2. If not found, list all available transcripts and pick the first one
         (non-English is fine — the LLM will handle translation)

    Args:
        video_id: The 11-character YouTube video ID.

    Returns:
        List of dicts with keys: text, start, duration.

    Raises:
        RuntimeError: With a user-friendly message describing the failure.
    """
    api = YouTubeTranscriptApi()

    # --- Attempt 1: fetch English transcript directly ---
    try:
        result = api.fetch(video_id, languages=["en"])
        return result.to_raw_data()
    except NoTranscriptFound:
        # English not available — try fallback below
        pass
    except TranscriptsDisabled:
        raise RuntimeError(
            f"Transcripts are disabled for video '{video_id}'. "
            "The video owner has turned off captions."
        )
    except VideoUnavailable:
        raise RuntimeError(
            f"Video '{video_id}' is unavailable. "
            "It may be private, deleted, or region-restricted."
        )
    except InvalidVideoId:
        raise RuntimeError(
            f"'{video_id}' is not a valid YouTube video ID."
        )
    except (RequestBlocked, IpBlocked):
        raise RuntimeError(
            "YouTube is blocking requests right now. "
            "This is usually temporary — please try again in a few minutes."
        )

    # --- Attempt 2: list all transcripts and pick the first available ---
    try:
        transcript_list = api.list(video_id)
        # Pick the first available transcript (any language)
        for transcript in transcript_list:
            result = transcript.fetch()
            return result.to_raw_data()
    except Exception:
        pass

    raise RuntimeError(
        f"Could not fetch any transcript for video '{video_id}'. "
        "The video may not have captions/subtitles available."
    )


def main():
    """Main entry point — read video ID from CLI args, fetch & print transcript."""

    # --- Validate CLI arguments ---
    if len(sys.argv) < 2:
        print("ERROR: No video ID or URL provided.", file=sys.stderr)
        print("Usage: python index.py <video_id_or_url>", file=sys.stderr)
        sys.exit(1)

    raw_input = sys.argv[1]

    # --- Extract video ID ---
    try:
        video_id = extract_video_id(raw_input)
    except ValueError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)

    # --- Fetch transcript (with cache) ---
    try:
        # Check cache first
        transcript_segments = get_cached_transcript(video_id)
        if transcript_segments is None:
            transcript_segments = fetch_transcript(video_id)
            save_to_cache(video_id, transcript_segments)
    except RuntimeError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        # Catch-all for unexpected network errors, timeouts, etc.
        print(f"ERROR: An unexpected error occurred: {e}", file=sys.stderr)
        sys.exit(1)

    # --- Format transcript ---
    formatted = format_transcript(transcript_segments)

    if not formatted:
        print("ERROR: Transcript was fetched but appears to be empty.", file=sys.stderr)
        sys.exit(1)

    # --- Chunk if needed ---
    chunks = chunk_transcript(formatted)

    # --- Output ---
    # If single chunk, print plain text
    # If multiple chunks, print as JSON object so the LLM knows it's chunked
    if len(chunks) == 1:
        print(chunks[0])
    else:
        output = {
            "video_id": video_id,
            "total_chunks": len(chunks),
            "note": "This transcript was split into chunks because the video is long. Process all chunks.",
            "chunks": chunks,
        }
        print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()

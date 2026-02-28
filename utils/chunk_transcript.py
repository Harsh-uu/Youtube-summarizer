"""
chunk_transcript.py
-------------------
Splits a long formatted transcript string into smaller chunks
so the LLM can process videos longer than ~30 minutes without
exceeding context limits.

Default chunk size: ~4000 characters (well within Gemini's limits,
leaves room for the summary prompt).
"""


def chunk_transcript(transcript_text: str, max_chars: int = 4000) -> list:
    """
    Split a formatted transcript into chunks of approximately max_chars.

    Splits on newline boundaries so we never cut a line in half.

    Args:
        transcript_text: The full formatted transcript string
                         (output of format_transcript).
        max_chars: Maximum characters per chunk (default 4000).

    Returns:
        A list of strings, each at most ~max_chars long.
        If the transcript fits in one chunk, returns a single-element list.
    """
    if not transcript_text:
        return []

    # If it already fits, return as-is
    if len(transcript_text) <= max_chars:
        return [transcript_text]

    chunks = []
    lines = transcript_text.split("\n")
    current_chunk = []
    current_length = 0

    for line in lines:
        line_length = len(line) + 1  # +1 for the newline character

        # If adding this line would exceed the limit, start a new chunk
        if current_length + line_length > max_chars and current_chunk:
            chunks.append("\n".join(current_chunk))
            current_chunk = []
            current_length = 0

        current_chunk.append(line)
        current_length += line_length

    # Don't forget the last chunk
    if current_chunk:
        chunks.append("\n".join(current_chunk))

    return chunks

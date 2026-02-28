---
name: youtube-summarizer
description: Summarizes YouTube videos and answers follow-up questions about them. Activate when the user sends a YouTube link or asks about a YouTube video.
---

# YouTube Summarizer & Q&A Skill

## When to Activate

Trigger this skill when:
- The user sends a message containing a YouTube URL (`youtube.com/watch?v=`, `youtu.be/`, `youtube.com/shorts/`, or similar)
- The user asks you to summarize a YouTube video
- The user asks a follow-up question about a video you already summarized in this session

## Step 1: Fetch the Transcript

When you detect a YouTube URL in the user's message, run the following shell command:

```
cd {baseDir} && .\venv\Scripts\python.exe index.py "<VIDEO_URL_OR_ID>"
```

Replace `<VIDEO_URL_OR_ID>` with the exact URL or video ID the user sent.

**Important:**
- Always use `.\venv\Scripts\python.exe` (the virtual environment Python), NOT the system `python`
- Pass the full URL or video ID as a single quoted argument
- The script prints the transcript to stdout. Capture the entire output.
- If the script prints an error (starts with "ERROR:"), relay that error to the user in a friendly way. Do NOT try to summarize without a transcript.

## Step 2: Generate the Summary

Once you have the transcript text, generate a structured summary in this exact format:

---

🎥 **Video Title**: _(Infer the title from the transcript content. If you cannot determine it, write "YouTube Video Summary")_

📌 **Key Points**:
1. [First key takeaway]
2. [Second key takeaway]
3. [Third key takeaway]
4. [Fourth key takeaway]
5. [Fifth key takeaway]

⏱ **Important Timestamps**:
- `[MM:SS]` — [What happens at this point]
- `[MM:SS]` — [What happens at this point]
- `[MM:SS]` — [What happens at this point]
- _(Include 3–5 meaningful timestamps from the transcript)_

🧠 **Core Takeaway**: [One sentence capturing the main message of the video]

---

**Rules for summaries:**
- Key points should be specific and informative, not vague
- Timestamps must come from the actual transcript data (use the `[MM:SS]` markers)
- Keep the summary concise — no more than ~300 words
- If the transcript is in a non-English language, still produce the summary in English by default (unless the user asks for another language)

## Step 3: Handle Follow-up Q&A

After summarizing a video, the user may ask follow-up questions about it. When they do:

1. **Answer ONLY from the transcript content.** Do not use outside knowledge or make things up.
2. If the answer is clearly covered in the transcript, provide it with the relevant timestamp: _"At [MM:SS], the speaker mentions that..."_
3. If the topic is NOT covered in the transcript, say exactly: **"This topic is not covered in the video."**
4. Do NOT hallucinate or speculate. Stick strictly to what the transcript says.
5. Keep answers concise but complete.

## Step 4: Language Support

- **Default language:** English
- If the user says "Summarize in Hindi", "Explain in Tamil", "Answer in Kannada", or requests any other language — provide the response in that language.
- If the original transcript is in a non-English language (e.g., Hindi), you can summarize in that language directly.
- Language preference persists for the session: if the user switches to Hindi, keep responding in Hindi until they switch back.
- Supported languages include but are not limited to: English, Hindi (हिन्दी), Tamil (தமிழ்), Kannada (ಕನ್ನಡ), Telugu (తెలుగు), Bengali (বাংলা), Marathi (मराठी).

## Error Handling

When things go wrong, respond helpfully:

| Error | Response |
|-------|----------|
| Invalid URL (not a YouTube link) | "That doesn't look like a YouTube link. Please send a valid YouTube URL (e.g., https://youtube.com/watch?v=...) and I'll summarize it for you." |
| No transcript available | "This video doesn't have captions/subtitles available, so I can't fetch the transcript. Try a different video that has captions enabled." |
| Video unavailable/private | "This video appears to be unavailable — it might be private, deleted, or region-restricted." |
| YouTube blocking requests | "YouTube is temporarily blocking transcript requests. Please try again in a few minutes." |
| Very long transcript (chunked) | Process ALL chunks. The output will be a JSON object with a `chunks` array — read every chunk before generating the summary. |

## Bonus Commands (if the user sends these)

- `/summary` — Re-display the last summary you generated in this session
- `/deepdive` — Provide a more detailed, section-by-section breakdown of the video
- `/actionpoints` — Extract action items, recommendations, or advice from the video
- `/lang <language>` — Switch response language (e.g., `/lang Hindi`)

## Important Reminders

- You do NOT call any external API for summarization — YOU are the summarizer (powered by your own LLM capabilities)
- The Python script ONLY fetches the transcript — all intelligence comes from you
- Never fabricate transcript content. If the fetch fails, say so honestly.
- Keep the session context: if the user already sent a video, they can ask questions about it without resending the link

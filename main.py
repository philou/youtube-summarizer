# Main script entry point for YouTube Channel Summarizer

import os
from dotenv import load_dotenv
import sys
import openai
from youtube_transcript_api import YouTubeTranscriptApi

def fetch_transcript(video_id):
    """Fetch transcript as a single string."""
    transcript = YouTubeTranscriptApi().fetch(video_id)
    return " ".join([entry['text'] for entry in transcript.to_raw_data()])

def summarize_text(text, api_key):
    openai.api_key = api_key
    client = openai.OpenAI()

    response = client.responses.create(
        model = "gpt-3.5-turbo",
        input = f"Summarize the following transcript:\n{text}"
    )
    return response.output_text

def main():
    load_dotenv()
    if len(sys.argv) < 2:
        print("Usage: python main.py <youtube_video_id>")
        sys.exit(1)
    video_id = sys.argv[1]
    if not video_id or len(video_id) != 11:
        print("Invalid YouTube video ID.")
        sys.exit(1)
    try:
        transcript = fetch_transcript(video_id)
    except Exception as e:
        print(f"Error fetching transcript: {e}")
        sys.exit(1)
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("OPENAI_API_KEY not set in environment.")
        sys.exit(1)
    try:
        summary = summarize_text(transcript, api_key)
    except Exception as e:
        print(f"Error summarizing transcript: {e}")
        sys.exit(1)
    print("\n--- Video Summary ---\n")
    print(summary)

if __name__ == "__main__":
    main()

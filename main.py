# Main script entry point for YouTube Channel Summarizer

import os
from dotenv import load_dotenv
import sys
import openai
from youtube_transcript_api import YouTubeTranscriptApi
import requests
import xml.etree.ElementTree as ET

def fetch_transcript(video_id):
    """Fetch transcript as a single string."""
    transcript = YouTubeTranscriptApi().fetch(video_id)
    return " ".join([entry['text'] for entry in transcript.to_raw_data()])

def get_latest_video_info_from_rss(rss_url):
    """Fetch the latest video ID from a YouTube channel RSS feed URL."""
    try:
        resp = requests.get(rss_url)
        resp.raise_for_status()
        root = ET.fromstring(resp.content)
        # YouTube RSS feeds use the 'yt:videoId' tag in the 'entry' element
        ns = {'yt': 'http://www.youtube.com/xml/schemas/2015', 'atom': 'http://www.w3.org/2005/Atom'}
        entry = root.find('atom:entry', ns)
        if entry is None:
            raise ValueError("No video entries found in RSS feed.")
        video_id_elem = entry.find('yt:videoId', ns)
        if video_id_elem is None:
            raise ValueError("No videoId found in latest entry.")
 
        title_elem = entry.find('atom:title', ns)
        if title_elem is None:
            raise ValueError("No title found in latest entry.")
 
        published_elem = entry.find('atom:published', ns)
        if published_elem is None:
            raise ValueError("No published found in latest entry.")

        return {
            "id": video_id_elem.text,
            "title": title_elem.text,
            "published": published_elem.text,
            "url": f"https://www.youtube.com/watch?v={video_id_elem.text}"
        }
    except Exception as e:
        raise RuntimeError(f"Failed to parse RSS feed: {e}")

def summarize_text(text, api_key):
    openai.api_key = api_key
    client = openai.OpenAI()

    response = client.responses.create(
        model = "gpt-3.5-turbo",
        input = f"Summarize the following transcript:\n{text}"
    )
    return response.output_text

def summarize_video(transcript, video_info, api_key):
    summary = summarize_text(transcript, api_key)

    markdown_summary = f"# {video_info['title']}\n\n"
    markdown_summary += summary
    markdown_summary += f"\n\n*Published on {video_info['published']} at {video_info['url']}*\n"

    return markdown_summary

def main():
    load_dotenv()
    if len(sys.argv) < 2:
        print("Usage: python main.py <youtube_channel_id>. See how to get the channel_id at https://webapps.stackexchange.com/questions/111680/how-to-find-channel-rss-feed-on-youtube")
        sys.exit(1)
    channel_id = sys.argv[1]
    if not channel_id or len(channel_id) != 24 or not channel_id.startswith("UC"):
        print("Invalid YouTube channel ID.")
        sys.exit(1)
    rss_url = f"https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}"
    try:
        video_info = get_latest_video_info_from_rss(rss_url)
    except Exception as e:
        print(f"Error fetching latest video ID: {e}")
        sys.exit(1)
    try:
        transcript = fetch_transcript(video_info["id"])
    except Exception as e:
        print(f"Error fetching transcript: {e}")
        sys.exit(1)
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("OPENAI_API_KEY not set in environment.")
        sys.exit(1)
    try:
        summary = summarize_video(transcript, video_info, api_key)
    except Exception as e:
        print(f"Error summarizing transcript: {e}")
        sys.exit(1)
    print(f"\n--- Video Summary for latest video ({video_info["id"]}) ---\n")
    print(summary)

if __name__ == "__main__":
    main()

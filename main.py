# Main script entry point for YouTube Channel Summarizer

import os
from dotenv import load_dotenv
import sys
import openai
from youtube_transcript_api import YouTubeTranscriptApi
import requests
import xml.etree.ElementTree as ET

class Summarizer:
    def __init__(self, api_key):
        self.api_key = api_key
        openai.api_key = self.api_key
    
    def summarize_text(self, text):
        client = openai.OpenAI()

        response = client.responses.create(
            model = "gpt-3.5-turbo",
            input = f"Summarize the following transcript:\n{text}"
        )
        return response.output_text


class YoutubeTranscription:
    def fetch(self, video_id):
        """Fetch transcript as a single string."""
        transcript = YouTubeTranscriptApi().fetch(video_id)
        return " ".join([entry['text'] for entry in transcript.to_raw_data()])

def channel_rss_url(channel_id):
    return f"https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}"

class YoutubeSummarizer:
    def get_latest_video_info_from_rss(self, rss_url):
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

    def summarize_video(self, transcript, video_info):
        summary = self.summarizer.summarize_text(transcript)

        markdown_summary = f"# {video_info['title']}\n\n"
        markdown_summary += summary
        markdown_summary += f"\n\n*Published on {video_info['published']} at {video_info['url']}*\n"

        return markdown_summary

    def run(self, channel_id):
        rss_url = channel_rss_url(channel_id)
        try:
            video_info = self.get_latest_video_info_from_rss(rss_url)
        except Exception as e:
            raise RuntimeError(f"Error fetching latest video ID: {e}")
        try:
            transcript = self.transcript_service.fetch(video_info["id"])
        except Exception as e:
            raise RuntimeError(f"Error fetching transcript: {e}")
        try:
            summary = self.summarize_video(transcript, video_info)
        except Exception as e:
            raise RuntimeError(f"Error summarizing transcript: {e}")

        print(f"--- Summarizing {video_info["title"]} ({video_info["id"]})\n")

        # Save summary to disk
        os.makedirs(channel_id, exist_ok=True)
        summary_file_path = os.path.join(channel_id, f"{video_info['id']}.md")
        with open(summary_file_path, 'w') as f:
            f.write(summary)

        
    def __init__(self, summarizer, transcripter):
        self.summarizer = summarizer
        self.transcript_service = transcripter

def main():
    try:
        if len(sys.argv) < 2:
            raise RuntimeError("Usage: python main.py <youtube_channel_id>. See how to get the channel_id at https://webapps.stackexchange.com/questions/111680/how-to-find-channel-rss-feed-on-youtube")
        channel_id = sys.argv[1]
        if not channel_id or len(channel_id) != 24 or not channel_id.startswith("UC"):
            raise RuntimeError("Invalid YouTube channel ID.")

        load_dotenv()
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY not set in environment.")

        YoutubeSummarizer(
            summarizer=Summarizer(api_key),
            transcripter=YoutubeTranscription()
        ).run(channel_id)

    except Exception as e:
        sys.stderr.write(f"Unexpected error: {e}\n")
        sys.exit(1)

if __name__ == "__main__":
    main()
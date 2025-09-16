# Main script entry point for YouTube Channel Summarizer

import os
from dotenv import load_dotenv
import sys
import openai
from youtube_transcript_api import YouTubeTranscriptApi
import requests
import xml.etree.ElementTree as ET
import yagmail

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
    def get_channel_title_and_video_infos(self, rss_url):
        """Fetch channel title and all video infos from a YouTube channel RSS feed URL."""
        try:
            resp = requests.get(rss_url)
            resp.raise_for_status()
            root = ET.fromstring(resp.content)
            ns = {'yt': 'http://www.youtube.com/xml/schemas/2015', 'atom': 'http://www.w3.org/2005/Atom'}

            # Channel title is the <title> directly under <feed>
            channel_title_elem = root.find('atom:title', ns)
            channel_title = channel_title_elem.text if channel_title_elem is not None else None

            entries = root.findall('atom:entry', ns)

            video_infos = []
            for entry in entries:
                video_id_elem = entry.find('yt:videoId', ns)
                if video_id_elem is None:
                    raise ValueError("No videoId found in entry.")

                title_elem = entry.find('atom:title', ns)
                if title_elem is None:
                    raise ValueError("No title found in entry.")
        
                published_elem = entry.find('atom:published', ns)
                if published_elem is None:
                    raise ValueError("No published found in entry.")

                video_infos.append({
                    "id": video_id_elem.text,
                    "title": title_elem.text,
                    "published": published_elem.text,
                    "url": f"https://www.youtube.com/watch?v={video_id_elem.text}"
                })

            return {"title": channel_title, "video_infos": video_infos}
        
        except Exception as e:
            raise RuntimeError(f"Failed to parse RSS feed: {e}")

    def summarize_video(self, transcript, video_info):
        summary = self.summarizer.summarize_text(transcript)

        markdown_summary = f"# {video_info['title']}\n\n"
        markdown_summary += summary
        markdown_summary += f"\n\n*Published on {video_info['published']} at {video_info['url']}*\n"

        return markdown_summary

    def run(self, channel_id, email, max_summaries=None):
        rss_url = channel_rss_url(channel_id)
        channel_info = self.get_channel_title_and_video_infos(rss_url)
        channel_title = channel_info["title"]
        video_infos = channel_info["video_infos"]
        print(f"Found {len(video_infos)} videos in channel {channel_id}.")

        video_infos = [vi for vi in video_infos if not self.is_summary_file_present(channel_id, vi)]
        if max_summaries is not None:
            video_infos = video_infos[:max_summaries]
        print(f"Summarizing {len(video_infos)} new videos...")

        summaries = []
        for video_info in video_infos:
            print(f"- Summarizing {video_info['title']} ({video_info['id']})\n")

            transcript = self.transcript_service.fetch(video_info["id"])
            summary = self.summarize_video(transcript, video_info)
            self.write_file(channel_id, video_info, summary)

            summaries.append(summary)

        print(f"Sending summary email to {email}...")

        combined_md = [f"#{md}" for md in summaries]
        summaries_markdown = "\n\n".join(combined_md).strip()
        full_markdown = ""
        if (len(video_infos) > 1):
            meta_summary = self.summarizer.summarize_text(summaries_markdown)
            full_markdown = '''\
# Summaries for channel {channel_title} ({channel_id})

## At a glance

{meta_summary}

{summaries_markdown}
'''.format(channel_title=channel_title, channel_id=channel_id, meta_summary=meta_summary, summaries_markdown=summaries_markdown)

        else:
            full_markdown = '''\
# Summaries for channel {channel_title} ({channel_id})

{summaries_markdown}
'''.format(channel_title=channel_title, channel_id=channel_id, summaries_markdown=summaries_markdown)
            
        self.email_service.send(email, f"[{channel_title}] New Video Summaries Available", full_markdown)

    def is_summary_file_present(self, channel_id, video_info):
        return os.path.exists(self.summary_file_path(channel_id, video_info))

    def summary_file_path(self, channel_id, video_info):
        return os.path.join(channel_id, self.summary_file_name(video_info))

    def write_file(self, channel_id, video_info, summary):
        os.makedirs(channel_id, exist_ok=True)
        summary_file_path = os.path.join(channel_id, self.summary_file_name(video_info))
        with open(summary_file_path, 'w') as f:
            f.write(summary)

    def summary_file_name(self, video_info):
        return f"{video_info['id']}.md"
        
    def __init__(self, summarizer, transcripter, email_service):
        self.summarizer = summarizer
        self.transcript_service = transcripter
        self.email_service = email_service

def main():
    try:
        channel_id, recipient_email, max_summaries = parse_arguments()

        api_key, gmail_username, gmail_password = load_environment_variables()
        
        YoutubeSummarizer(
            summarizer=Summarizer(api_key),
            transcripter=YoutubeTranscription(),
            email_service=yagmail.SMTP(gmail_username, gmail_password)
        ).run(channel_id, recipient_email, max_summaries)

    except Exception as e:
        sys.stderr.write(f"Unexpected error: {e}\n")
        sys.exit(1)

def parse_arguments():
    if len(sys.argv) < 3:
        raise RuntimeError("Usage: python main.py <youtube_channel_id> <recipient_email>")
    channel_id = sys.argv[1]
    if not channel_id or len(channel_id) != 24 or not channel_id.startswith("UC"):
        raise RuntimeError("Invalid YouTube channel ID.")
    recipient_email = sys.argv[2]
    if not recipient_email:
        raise RuntimeError("Invalid recipient email.")

    max_summaries = None
    if len(sys.argv) > 3:
        max_summaries = int(sys.argv[3])
    return channel_id,recipient_email,max_summaries

def load_environment_variables():
    load_dotenv()

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY not set in environment.")

    gmail_username = os.getenv("GMAIL_USERNAME")
    if not gmail_username:
        raise RuntimeError("GMAIL_USERNAME not set in environment.")
    gmail_password = os.getenv("GMAIL_PASSWORD")
    if not gmail_password:
        raise RuntimeError("GMAIL_PASSWORD not set in environment.")

    return api_key, gmail_username, gmail_password

if __name__ == "__main__":
    main()
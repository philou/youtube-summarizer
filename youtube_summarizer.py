# Main script entry point for YouTube Channel Summarizer

import os
from dotenv import load_dotenv
import sys
import openai
from youtube_transcript_api import YouTubeTranscriptApi
import requests
import xml.etree.ElementTree as ET
import yagmail
import markdown
import subprocess
import time

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

class GitRepository:
    def commit_and_push(self, folder_path, commit_message):
        try:
            subprocess.run(['git', 'add', folder_path], check=True)
            subprocess.run(['git', 'commit', '-m', commit_message], check=True)
            subprocess.run(['git', 'push'], check=True)
            return True
        except subprocess.CalledProcessError as e:
            print(f"Git operation failed: {e}")
            return False

def channel_rss_url(channel_id):
    return f"https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}"

class YoutubeSummarizer:
        
    def __init__(self, summarizer, transcripter, email_service, git_repo, wait_between_requests=30):
        self.summarizer = summarizer
        self.transcript_service = transcripter
        self.email_service = email_service
        self.git_repo = git_repo
        self.wait_between_requests = wait_between_requests

    def run(self, channel_id_or_file_path, email, commit_summaries=False, max_summaries=None):
        # Get XML feed string from either local file or URL
        xml_feed_string = self.__get_channel_feed_xml_string(channel_id_or_file_path)
        
        # Extract common data from channel_info
        channel_info = self.__get_channel_title_and_videos_infos_from_xml(xml_feed_string)
        channel_id = channel_info["channel_id"]
        channel_title = channel_info["title"]
        video_infos = channel_info["video_infos"]
        
        print(f"Found {len(video_infos)} videos in channel {channel_id}.")

        video_infos = [vi for vi in video_infos if not self.__is_summary_file_present(channel_id, vi)]
        if max_summaries is not None:
            video_infos = video_infos[:max_summaries]

        if len(video_infos) == 0:
            print("No new videos to summarize.")
            return

        print(f"Summarizing {len(video_infos)} new videos...")
        summaries = []
        for video_info in video_infos:
            print(f"- Summarizing {video_info['title']} ({video_info['id']})\n")

            transcript = self.transcript_service.fetch(video_info["id"])
            summary = self.__summarize_video(transcript, video_info)
            self.__write_file(channel_id, video_info, summary)

            summaries.append(summary)

            # pause between requests to avoid rate limiting
            time.sleep(self.wait_between_requests)

        print(f"Sending summary email to {email}...")
        self.__send_email(email, channel_title, summaries)

        if commit_summaries:
            print("Committing summaries to git...")
            self.git_repo.commit_and_push(channel_id, f"Add summaries for {len(video_infos)} videos from channel {channel_title}")

    def __get_channel_feed_xml_string(self, channel_id_or_file_path):
        """Get XML feed string either from local file or by fetching from URL."""

        if channel_id_or_file_path.endswith(".xml") and os.path.isfile(channel_id_or_file_path):

            print(f"Processing local RSS feed file: {channel_id_or_file_path}")
            with open(channel_id_or_file_path, 'r', encoding='utf-8') as f:
                xml_feed_string = f.read()

        elif channel_id_or_file_path.startswith("UC") and len(channel_id_or_file_path) == 24:

            rss_url = channel_rss_url(channel_id_or_file_path)
            resp = requests.get(rss_url)
            resp.raise_for_status()
            xml_feed_string = resp.content

        else:
            raise RuntimeError(f"Invalid input: '{channel_id_or_file_path}'. Expected either a YouTube channel ID (starts with 'UC' and 24 characters long) or an XML file path (ends with '.xml').")
        
        return xml_feed_string

    def __get_channel_title_and_videos_infos_from_xml(self, xml_feed_string):
        """Extract channel title, video infos, and channel ID from XML root element."""
        try:
            root = ET.fromstring(xml_feed_string)
            ns = {'yt': 'http://www.youtube.com/xml/schemas/2015', 'atom': 'http://www.w3.org/2005/Atom'}

            # Extract channel ID from the RSS feed
            channel_id_elem = root.find('yt:channelId', ns)
            if channel_id_elem is None:
                raise ValueError("No channelId found in RSS feed.")
            channel_id = "UC" + channel_id_elem.text

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

            return {"title": channel_title, "video_infos": video_infos, "channel_id": channel_id}
        
        except Exception as e:
            raise RuntimeError(f"Failed to parse RSS feed XML: {e}")


    def __summarize_video(self, transcript, video_info):
        summary = self.summarizer.summarize_text(transcript)

        markdown_summary = f"# {video_info['title']}\n\n"
        markdown_summary += summary
        markdown_summary += f"\n\n*Published on {video_info['published']} at {video_info['url']}*\n"

        return markdown_summary

    def __send_email(self, email, channel_title, summaries):
        full_markdown = self.__generate_email_content(channel_title, summaries)

        html_content = markdown.markdown(full_markdown)

        self.email_service.send(email, f"🎬 [YouTube Summaries][{channel_title}] {self.email_subject_detail(summaries)}", html_content)

    def email_subject_detail(self, summaries):
        if len(summaries) == 1:
            # Extract the title from the first line of the single summary
            return summaries[0].split('\n', 1)[0].lstrip('# ').strip()
        
        return f"{len(summaries)} New Video Summaries Available"

    def __generate_email_content(self, channel_title, summaries):
        combined_md = [f"#{md}" for md in summaries]
        summaries_markdown = "\n\n".join(combined_md).strip()
        full_markdown = ""
        meta_summary_md = ""
        if (len(summaries) > 1):
            meta_summary = self.summarizer.summarize_text(summaries_markdown)
            meta_summary_md = f"\n## At a glance\n\n{meta_summary}\n"
        
        full_markdown = f"# Summaries for channel {channel_title}\n{meta_summary_md}\n{summaries_markdown}"

        return full_markdown

    def __is_summary_file_present(self, channel_id, video_info):
        return os.path.exists(self.__summary_file_path(channel_id, video_info))

    def __summary_file_path(self, channel_id, video_info):
        return os.path.join(channel_id, self.__summary_file_name(video_info))

    def __write_file(self, channel_id, video_info, summary):
        os.makedirs(channel_id, exist_ok=True)
        summary_file_path = os.path.join(channel_id, self.__summary_file_name(video_info))
        with open(summary_file_path, 'w') as f:
            f.write(summary)

    def __summary_file_name(self, video_info):
        return f"{video_info['id']}.md"

def main():
    try:
        channel_id_or_file_path, recipient_email, max_summaries, git_commits_enabled = parse_arguments()

        api_key, gmail_username, gmail_password = load_environment_variables()
                
        YoutubeSummarizer(
            summarizer=Summarizer(api_key),
            transcripter=YoutubeTranscription(),
            email_service=yagmail.SMTP(gmail_username, gmail_password),
            git_repo=GitRepository()
        ).run(channel_id_or_file_path, recipient_email, 
              commit_summaries=git_commits_enabled, 
              max_summaries=max_summaries)

    except Exception as e:
        sys.stderr.write(f"Unexpected error: {e}\n")
        sys.exit(1)

def parse_arguments():
    if len(sys.argv) < 4:
        raise RuntimeError("Usage: python main.py <youtube_channel_id_or_file_path> <recipient_email> <--git-commits-on|--git-commits-off> [max_summaries]")

    channel_id_or_file_path = sys.argv[1]
    if not channel_id_or_file_path:
        raise RuntimeError("Invalid channel ID or file path.")

    recipient_email = sys.argv[2]
    if not recipient_email:
        raise RuntimeError("Invalid recipient email.")

    git_arg = sys.argv[3]
    if git_arg == "--git-commits-on":
        git_commits_enabled = True
    elif git_arg == "--git-commits-off":
        git_commits_enabled = False
    else:
        raise RuntimeError("Third argument must be --git-commits-on or --git-commits-off")

    max_summaries = None
    if len(sys.argv) == 5:
        try:
            max_summaries = int(sys.argv[4])
            if max_summaries < 1:
                raise ValueError()
        except ValueError:
            raise RuntimeError("max_summaries must be a positive integer")
    elif len(sys.argv) > 5:
        raise RuntimeError("Too many arguments. Expected at most 4 arguments.")

    return channel_id_or_file_path, recipient_email, max_summaries, git_commits_enabled

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
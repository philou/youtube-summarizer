import unittest
from approvaltests import verify
from approvaltests.namer.default_namer_factory import NamerFactory
import os
from youtube_summarizer import YoutubeSummarizer, channel_rss_url
from faker import Faker
import responses
from pyfakefs.fake_filesystem_unittest import Patcher
from datetime import datetime, timedelta
import re

TEST_CHANNEL_ID = "UC_could_be_anything____"

class FakeSummarizer:
    def summarize_text(self, text):
        # demarkdownify text using
        text = re.sub(r'#+ ', '', text).strip()

        words = text.split()
        if len(words) <= 10:
            return text
        first10 = ' '.join(words[:10])
        remaining = len(words) - 10
        return f"{first10}... and {remaining} more words"
    
class FakeTranscription:
    def fetch(self, video_id):
        Faker.seed(video_id)
        fake = Faker()
        return video_id + " " + fake.text(max_nb_chars=200)
    
class FakeEmailService:
    def __init__(self):
        self.sent_email = None

    def send(self, to, subject, body):
        self.sent_email = {
            'to': to,
            'subject': subject,
            'body': body
        }

def build_video_ids(count):
    """Build a list of simple video IDs"""
    return [str(i) for i in range(1, count + 1)]

def generate_title_for_video_id(video_id):
    """Generate deterministic title from video ID using faker"""
    Faker.seed(int(video_id))
    fake = Faker()
    return fake.sentence(nb_words=6).rstrip('.')

def generate_published_date(video_id):
    """Generate published date: 2025-09-12 minus video_id days"""
    base_date = datetime(2025, 9, 12)
    days_to_subtract = int(video_id)
    published_date = base_date - timedelta(days=days_to_subtract)
    return published_date.strftime('%Y-%m-%dT%H:%M:%S+00:00')

def generate_feed_for(video_ids, channel_title = "My Channel"):
    """Generate RSS feed XML for given video IDs"""
    entries = []
    for video_id in video_ids:
        title = generate_title_for_video_id(video_id)
        published = generate_published_date(video_id)
        entries.append(f'''
                    <entry>
                        <yt:videoId>{video_id}</yt:videoId>
                        <title>{title}</title>
                        <published>{published}</published>
                    </entry>''')
    
    return f'''<?xml version="1.0" encoding="UTF-8"?>
            <feed xmlns:yt="http://www.youtube.com/xml/schemas/2015" xmlns:media="http://search.yahoo.com/mrss/" xmlns="http://www.w3.org/2005/Atom">
                <title>{channel_title}</title>
                {''.join(entries)}
            </feed>'''

class TestYouTubeSummarizerE2E(unittest.TestCase):

    def setUp(self):
        responses.reset()

    def tearDown(self):
        responses.reset()

    @responses.activate
    def test_saves_a_summary_in_a_channel_folder(self):
        """Test that given a channel id, the summary is saved to an md file in a folder named after the channel id"""

        video_ids = build_video_ids(1)
        responses.get(channel_rss_url(TEST_CHANNEL_ID),
                body=generate_feed_for(video_ids))

        content = ""

        with Patcher():
            YoutubeSummarizer(FakeSummarizer(), FakeTranscription(), FakeEmailService()).run(TEST_CHANNEL_ID, "user@example.com")
            content = self.read_summary_md_file(TEST_CHANNEL_ID, video_ids[0])
            
        verify(content)

    @responses.activate
    def test_saves_many_summaries_in_a_channel_folder(self):
        """Test that the summaries are saved to md files in a folder named after the channel id"""

        video_ids = build_video_ids(2)
        responses.get(channel_rss_url(TEST_CHANNEL_ID),
                body=generate_feed_for(video_ids))

        summary1 = ""
        summary2 = ""

        with Patcher():
            YoutubeSummarizer(FakeSummarizer(), FakeTranscription(), FakeEmailService()).run(TEST_CHANNEL_ID, "user@example.com")
            summary1 = self.read_summary_md_file(TEST_CHANNEL_ID, video_ids[0])
            summary2 = self.read_summary_md_file(TEST_CHANNEL_ID, video_ids[1])

        verify(summary1, options=NamerFactory.with_parameters("summary 1"))
        verify(summary2, options=NamerFactory.with_parameters("summary 2"))

    @responses.activate
    def test_only_writes_missing_summaries(self):
        """Test that only missing summaries are written to md files in a folder named after the channel id"""

        video_ids = build_video_ids(2)
        responses.get(channel_rss_url(TEST_CHANNEL_ID),
                body=generate_feed_for(video_ids))

        with Patcher() as patcher:
            existing_summary = "existing summary"
            self.write_summary_file(video_ids[0], existing_summary)

            YoutubeSummarizer(FakeSummarizer(), FakeTranscription(), FakeEmailService()).run(TEST_CHANNEL_ID, "user@example.com")

            self.assertTrue(self.is_summary_file_present(video_ids[1]))
            self.assertEqual(existing_summary, self.read_summary_md_file(TEST_CHANNEL_ID, video_ids[0]))


    @responses.activate
    def test_only_writes_so_many_summaries(self):
        """Test that it only writes as many summaries as asked"""

        video_ids = build_video_ids(2)
        responses.get(channel_rss_url(TEST_CHANNEL_ID),
                body=generate_feed_for(video_ids))

        with Patcher() as patcher:
            YoutubeSummarizer(FakeSummarizer(), FakeTranscription(), FakeEmailService()).run(TEST_CHANNEL_ID, "user@example.com", 1)

            self.assertTrue(self.is_summary_file_present(video_ids[0]))
            self.assertFalse(self.is_summary_file_present(video_ids[1]))

    @responses.activate
    def test_shares_new_summaries_through_email(self):
        """Test that new summaries are shared through email"""

        video_ids = build_video_ids(1)
        responses.get(channel_rss_url(TEST_CHANNEL_ID),
                body=generate_feed_for(video_ids))

        fakeEmailer = FakeEmailService()

        with Patcher() as patcher:
            YoutubeSummarizer(FakeSummarizer(), FakeTranscription(), fakeEmailer).run(TEST_CHANNEL_ID, "johndoe@example.com", 1)

        self.assertEqual('johndoe@example.com', fakeEmailer.sent_email['to'])
        verify(fakeEmailer.sent_email['body'])

    @responses.activate
    def test_create_summary_of_summaries_if_there_is_more_than_one_video(self):
        """Test that a summary of summaries is created and shared through email"""

        video_ids = build_video_ids(2)
        responses.get(channel_rss_url(TEST_CHANNEL_ID),
                body=generate_feed_for(video_ids))

        fakeEmailer = FakeEmailService()

        with Patcher() as patcher:
            YoutubeSummarizer(FakeSummarizer(), FakeTranscription(), fakeEmailer).run(TEST_CHANNEL_ID, "user@example.com")

        verify(fakeEmailer.sent_email['body'])

    @responses.activate
    def test_email_subject_contains_number_of_video_summaries(self):
        """Test that the email subject contains the number of new video summaries"""

        video_ids = build_video_ids(2)
        responses.get(channel_rss_url(TEST_CHANNEL_ID),
                body=generate_feed_for(video_ids, "Dog Channel"))

        fakeEmailer = FakeEmailService()

        with Patcher() as patcher:
            YoutubeSummarizer(FakeSummarizer(), FakeTranscription(), fakeEmailer).run(TEST_CHANNEL_ID, "user@example.com")

        self.assertEqual(
            "🎬 [YouTube Summaries][Dog Channel] 2 New Video Summaries Available",
            fakeEmailer.sent_email['subject'])

    @responses.activate
    def test_uses_video_title_as_email_subject_if_only_one_new_video(self):
        """Test that if there is only one new video, the email subject is the video title"""

        video_ids = build_video_ids(1)
        responses.get(channel_rss_url(TEST_CHANNEL_ID),
                body=generate_feed_for(video_ids, "Kitten Channel"))

        fakeEmailer = FakeEmailService()

        with Patcher() as patcher:
            YoutubeSummarizer(FakeSummarizer(), FakeTranscription(), fakeEmailer).run(TEST_CHANNEL_ID, "user@example.com")

        self.assertEqual(
            f"🎬 [YouTube Summaries][Kitten Channel] {generate_title_for_video_id(video_ids[0])}",
            fakeEmailer.sent_email['subject'])

    def is_summary_file_present(self, video_id):
        return os.path.exists(self.summary_file_path(TEST_CHANNEL_ID, video_id))

    def read_summary_md_file(self, channel_id, video_id):
        with open(self.summary_file_path(channel_id, video_id), 'r') as f:
            content = f.read()
        return content
    
    def write_summary_file(self, video_id, existing_summary):
        os.makedirs(TEST_CHANNEL_ID, exist_ok=True)
        with open(self.summary_file_path(TEST_CHANNEL_ID, video_id), 'w') as f:
            f.write(existing_summary)

    def summary_file_path(self, channel_id, video_id):
        return os.path.join(channel_id, video_id + '.md')

if __name__ == '__main__':
    unittest.main()

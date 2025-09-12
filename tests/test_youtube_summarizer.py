import unittest
from approvaltests import verify, approvals
from approvaltests.namer.default_namer_factory import NamerFactory
import os
from main import YoutubeSummarizer, channel_rss_url
from faker import Faker
import responses
from pyfakefs.fake_filesystem_unittest import Patcher

TEST_CHANNEL_ID = "UC_could_be_anything____"

class FakeSummarizer:
    def summarize_text(self, text):
        return text[:30] + '...'
    
class FakeTranscription:
    def fetch(self, video_id):
        Faker.seed(video_id)
        fake = Faker()
        return video_id + " " + fake.text(max_nb_chars=200)

class TestYouTubeSummarizerE2E(unittest.TestCase):

    def setUp(self):
        responses.reset()

    def tearDown(self):
        responses.reset()

    @responses.activate
    def test_saves_a_summary_in_a_channel_folder(self):
        """Test that given a channel id, the summary is saved to an md file in a folder named after the channel id"""

        responses.get(channel_rss_url(TEST_CHANNEL_ID),
                body='''<?xml version="1.0" encoding="UTF-8"?>
                <feed xmlns:yt="http://www.youtube.com/xml/schemas/2015" xmlns:media="http://search.yahoo.com/mrss/" xmlns="http://www.w3.org/2005/Atom">
                    <entry>
                        <yt:videoId>Nx6qX-9tim4</yt:videoId>
                        <title>070 - Why ME/CFS &quot;fatigue&quot; is not normal fatigue</title>
                        <published>2025-08-25T13:29:58+00:00</published>
                    </entry>
                </feed>''')

        content = ""

        with Patcher():
            YoutubeSummarizer(FakeSummarizer(), FakeTranscription()).run(TEST_CHANNEL_ID)
            content = self.read_summary_md_file(TEST_CHANNEL_ID, 'Nx6qX-9tim4')
            
        verify(content)

    @responses.activate
    def test_saves_many_summaries_in_a_channel_folder(self):
        """Test that given a channel id, the summaries are saved to md files in a folder named after the channel id"""

        responses.get(channel_rss_url(TEST_CHANNEL_ID),
                body='''<?xml version="1.0" encoding="UTF-8"?>
                <feed xmlns:yt="http://www.youtube.com/xml/schemas/2015" xmlns:media="http://search.yahoo.com/mrss/" xmlns="http://www.w3.org/2005/Atom">
                    <entry>
                        <yt:videoId>Nx6qX-9tim4</yt:videoId>
                        <title>070 - Why ME/CFS &quot;fatigue&quot; is not normal fatigue</title>
                        <published>2025-08-25T13:29:58+00:00</published>
                    </entry>
                    <entry>
                        <yt:videoId>zN8fdhm6Kdw</yt:videoId>
                        <title>069 - Can saline infusions help ME/CFS?</title>
                        <published>2025-08-18T18:06:48+00:00</published>
                    </entry>
                </feed>''')

        summary1 = ""
        summary2 = ""

        with Patcher():
            YoutubeSummarizer(FakeSummarizer(), FakeTranscription()).run(TEST_CHANNEL_ID)
            summary1 = self.read_summary_md_file(TEST_CHANNEL_ID, 'Nx6qX-9tim4')
            summary2 = self.read_summary_md_file(TEST_CHANNEL_ID, 'zN8fdhm6Kdw')

        verify(summary1, options=NamerFactory.with_parameters("summary 1"))
        verify(summary2, options=NamerFactory.with_parameters("summary 2"))

    @responses.activate
    def test_only_writes_missing_summaries(self):
        """Test that given a channel id, only missing summaries are written to md files in a folder named after the channel id"""

        responses.get(channel_rss_url(TEST_CHANNEL_ID),
                body='''<?xml version="1.0" encoding="UTF-8"?>
                <feed xmlns:yt="http://www.youtube.com/xml/schemas/2015" xmlns:media="http://search.yahoo.com/mrss/" xmlns="http://www.w3.org/2005/Atom">
                    <entry>
                        <yt:videoId>Nx6qX-9tim4</yt:videoId>
                        <title>070 - Why ME/CFS &quot;fatigue&quot; is not normal fatigue</title>
                        <published>2025-08-25T13:29:58+00:00</published>
                    </entry>
                    <entry>
                        <yt:videoId>zN8fdhm6Kdw</yt:videoId>
                        <title>069 - Can saline infusions help ME/CFS?</title>
                        <published>2025-08-18T18:06:48+00:00</published>
                    </entry>
                </feed>''')

        with Patcher() as patcher:
            existing_summary = "existing summary"
            self.write_summary_file('Nx6qX-9tim4', existing_summary)

            YoutubeSummarizer(FakeSummarizer(), FakeTranscription()).run(TEST_CHANNEL_ID)

            self.assertTrue(self.is_summary_file_present('zN8fdhm6Kdw'))
            self.assertEqual(existing_summary, self.read_summary_md_file(TEST_CHANNEL_ID, 'Nx6qX-9tim4'))


    @responses.activate
    def test_only_writes_so_many_summaries(self):
        """Test that given a channel id, only writes as many summaries as asked"""

        responses.get(channel_rss_url(TEST_CHANNEL_ID),
                body='''<?xml version="1.0" encoding="UTF-8"?>
                <feed xmlns:yt="http://www.youtube.com/xml/schemas/2015" xmlns:media="http://search.yahoo.com/mrss/" xmlns="http://www.w3.org/2005/Atom">
                    <entry>
                        <yt:videoId>Nx6qX-9tim4</yt:videoId>
                        <title>070 - Why ME/CFS &quot;fatigue&quot; is not normal fatigue</title>
                        <published>2025-08-25T13:29:58+00:00</published>
                    </entry>
                    <entry>
                        <yt:videoId>zN8fdhm6Kdw</yt:videoId>
                        <title>069 - Can saline infusions help ME/CFS?</title>
                        <published>2025-08-18T18:06:48+00:00</published>
                    </entry>
                </feed>''')

        with Patcher() as patcher:
            YoutubeSummarizer(FakeSummarizer(), FakeTranscription()).run(TEST_CHANNEL_ID, 1)

            self.assertTrue(self.is_summary_file_present('Nx6qX-9tim4'))
            self.assertFalse(self.is_summary_file_present('zN8fdhm6Kdw'))

    def is_summary_file_present(self, video_id='zN8fdhm6Kdw'):
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

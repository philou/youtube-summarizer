import unittest
from approvaltests import verify
import os
from main import YoutubeSummarizer, channel_rss_url
from faker import Faker
import responses
from pyfakefs.fake_filesystem_unittest import Patcher

TEST_CHANNEL_ID = "UCoVoOvIX90IMEZCbBf_ycEA"

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
        # Start response recorder with saved responses
        responses.get(channel_rss_url(TEST_CHANNEL_ID),
                      body='''<?xml version="1.0" encoding="UTF-8"?>
                        <feed xmlns:yt="http://www.youtube.com/xml/schemas/2015" xmlns:media="http://search.yahoo.com/mrss/" xmlns="http://www.w3.org/2005/Atom">
                            <entry>
                                <yt:videoId>Nx6qX-9tim4</yt:videoId>
                                <title>070 - Why ME/CFS &quot;fatigue&quot; is not normal fatigue</title>
                                <published>2025-08-25T13:29:58+00:00</published>
                            </entry>
                        </feed>''')

    @responses.activate
    def test_saves_summaries_in_folder_on_disk(self):
        """Test that given a channel id, the summary is saved to an md file in a folder named after the channel id"""

        content = ""

        with Patcher():
            YoutubeSummarizer(FakeSummarizer(), FakeTranscription()).run(TEST_CHANNEL_ID)

            # check that there is a folder named after the channel id
            self.assertTrue(os.path.exists(TEST_CHANNEL_ID))

            # check that there is a file named <video_id>.md in the folder
            files = os.listdir(TEST_CHANNEL_ID)
            self.assertEqual(len(files), 1)
            self.assertEqual(files[0], 'Nx6qX-9tim4.md')

            ## load the content of the file in a string and approve it
            with open(os.path.join(TEST_CHANNEL_ID, files[0]), 'r') as f:
                content = f.read()
            
        verify(content)

if __name__ == '__main__':
    unittest.main()

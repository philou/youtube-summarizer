import unittest
from approvaltests import verify
from approvaltests.reporters import DiffReporter
import sys
from io import StringIO
from main import YoutubeSummarizer, channel_rss_url, main
from faker import Faker
import responses

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
    def test_process_channel_approved(self):
        # Set up test channel ID
        sys.argv = ['main.py', TEST_CHANNEL_ID]
        # Capture stdout
        stdout = StringIO()

        # Run the main function
        YoutubeSummarizer(FakeSummarizer(), FakeTranscription()).run(stdout)

        # Get the captured output
        output = stdout.getvalue()
        
        # Verify the output matches approved version
        verify(output, reporter=DiffReporter())


if __name__ == '__main__':
    unittest.main()

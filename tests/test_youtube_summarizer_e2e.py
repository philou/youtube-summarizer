import unittest
from approvaltests import verify
from approvaltests.reporters import DiffReporter
import sys
from io import StringIO
from main import YoutubeSummarizer, Summarizer

class FakeSummarizer:
    def summarize_text(self, text):
        return text[:20] + '...'

class TestYouTubeSummarizerE2E(unittest.TestCase):
    def setUp(self):
        # Capture stdout
        self.held, sys.stdout = sys.stdout, StringIO()

    def tearDown(self):
        # Restore stdout
        sys.stdout = self.held

    def test_process_channel_approved(self):
        """Test the full pipeline with actual YouTube and OpenAI services."""
        # Set up test channel ID
        test_channel = "UCoVoOvIX90IMEZCbBf_ycEA"
        sys.argv = ['main.py', test_channel]

        # Run the main function
        try:
            YoutubeSummarizer(FakeSummarizer()).main()

        except SystemExit:
            pass  # main() calls sys.exit(), which we want to catch

        # Get the captured output
        output = sys.stdout.getvalue()
        
        # Verify the output matches approved version
        verify(output, reporter=DiffReporter())

if __name__ == '__main__':
    unittest.main()

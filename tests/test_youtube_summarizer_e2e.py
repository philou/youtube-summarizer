import unittest
import sys
from youtube_summarizer import main

TEST_CHANNEL_ID = "UCoVoOvIX90IMEZCbBf_ycEA"

class TestYouTubeSummarizerE2E(unittest.TestCase):

    @unittest.skip("Skip by default. Potentially slow and expensive.")
    def test_smoke_e2e_with_real_services(self):
        """Just ensure no exception is raised with real services, using a known channel with recent videos."""
    
        try:
            sys.argv = ['main.py', TEST_CHANNEL_ID, "1"]
            main()
        except SystemExit as e:
            raise RuntimeError(f"Unexpected SystemExit: {e}")

        # expect no exception

if __name__ == '__main__':
    unittest.main()

import unittest
import sys
from main import main

TEST_CHANNEL_ID = "UCoVoOvIX90IMEZCbBf_ycEA"

class TestYouTubeSummarizerE2E(unittest.TestCase):

    @unittest.skip("Skip by default. Run with -k real_services to execute this test")
    def test_smoke_e2e_with_real_services(self):
        """Just ensure no exception is raised with real services, using a known channel with recent videos."""
    
        try:
            sys.argv = ['main.py', TEST_CHANNEL_ID]
            main()
        except SystemExit as e:
            raise RuntimeError(f"Unexpected SystemExit: {e}")

        # expect no exception

if __name__ == '__main__':
    unittest.main()

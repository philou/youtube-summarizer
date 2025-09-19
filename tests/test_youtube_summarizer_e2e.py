import unittest
import sys
import subprocess
from faker import Faker
from youtube_summarizer import main

# how to get a channel id: https://keywordrecon.com/articles/how-to-view-youtube-channel-id/
TEST_CHANNEL_ID = "UC9V_-gqJsZNOy4v_HqbRz3w"

class TestYouTubeSummarizerE2E(unittest.TestCase):

    def setUp(self):
        """Set up test environment with git branch."""
        # Generate unique branch name with faker
        fake = Faker()
        self.branch_name = f"e2e_test_{fake.word()}_{fake.word()}"
        
        # Store original branch to restore later
        self.original_branch = subprocess.run(
            ['git', 'branch', '--show-current'], 
            capture_output=True, text=True, check=True
        ).stdout.strip()
        
        # Create and checkout test branch
        subprocess.run(['git', 'checkout', '-b', self.branch_name], check=True)

        # Push it upstream
        subprocess.run(['git', 'push', '--set-upstream', 'origin', self.branch_name], check=True)

    def tearDown(self):
        """Clean up test environment by removing git branch."""
        # Clean up: switch back to original branch
        subprocess.run(['git', 'checkout', self.original_branch], check=True)
        
        # Delete the test branch locally
        subprocess.run(['git', 'branch', '-D', self.branch_name], check=True)
        
        # Delete the branch from remote if it was pushed
        try:
            subprocess.run(['git', 'push', 'origin', '--delete', self.branch_name], 
                         check=True, capture_output=True)
        except subprocess.CalledProcessError:
            # Branch might not have been pushed, ignore error
            pass

    @unittest.skip("Skip by default. Potentially slow and expensive.")
    def test_smoke_e2e_with_real_services(self):
        """Just ensure no exception is raised with real services, using a known channel with recent videos."""
        
        try:
            # Run the test with git commits enabled
            sys.argv = ['main.py', TEST_CHANNEL_ID, "philippe.bourgau@gmail.com", "--git-commits-on", "2"]
            main()
            
        except SystemExit as e:
            raise RuntimeError(f"Unexpected SystemExit: {e}")

        # expect no exception

if __name__ == '__main__':
    unittest.main()

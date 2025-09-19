import unittest
import sys
import subprocess
from faker import Faker
from youtube_summarizer import main

TEST_CHANNEL_ID = "UCoVoOvIX90IMEZCbBf_ycEA"

class TestYouTubeSummarizerE2E(unittest.TestCase):

    @unittest.skip("Skip by default. Potentially slow and expensive.")
    def test_smoke_e2e_with_real_services(self):
        """Just ensure no exception is raised with real services, using a known channel with recent videos."""
        
        # Generate unique branch name with faker
        fake = Faker()
        branch_name = f"e2e_test_{fake.word()}_{fake.word()}"
        
        # Store original branch to restore later
        original_branch = subprocess.run(
            ['git', 'branch', '--show-current'], 
            capture_output=True, text=True, check=True
        ).stdout.strip()
        
        try:
            # Create and checkout test branch
            subprocess.run(['git', 'checkout', '-b', branch_name], check=True)
            
            # Run the test with git commits enabled
            sys.argv = ['main.py', TEST_CHANNEL_ID, "philippe.bourgau@gmail.com", "--git-commits-on", "2"]
            main()
            
        except SystemExit as e:
            raise RuntimeError(f"Unexpected SystemExit: {e}")
        
        finally:
            # Clean up: switch back to original branch
            subprocess.run(['git', 'checkout', original_branch], check=True)
            
            # Delete the test branch locally
            subprocess.run(['git', 'branch', '-D', branch_name], check=True)
            
            # Delete the branch from remote if it was pushed
            try:
                subprocess.run(['git', 'push', 'origin', '--delete', branch_name], 
                             check=True, capture_output=True)
            except subprocess.CalledProcessError:
                # Branch might not have been pushed, ignore error
                pass

        # expect no exception

if __name__ == '__main__':
    unittest.main()

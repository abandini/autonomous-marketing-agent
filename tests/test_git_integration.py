"""
Tests for the Git integration and website updater.
"""

import os
import unittest
import tempfile
import shutil
from unittest.mock import MagicMock, patch

from core.git.git_integration import GitIntegration
from core.git.website_updater import WebsiteUpdater

class TestGitIntegration(unittest.TestCase):
    """Test cases for the Git integration module."""
    
    def setUp(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp()
        self.repo_url = "https://github.com/example/website.git"
        self.git = GitIntegration(
            repo_url=self.repo_url,
            local_path=self.test_dir,
            username="test_user",
            token="test_token"
        )
        
    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.test_dir, ignore_errors=True)
        
    @patch('subprocess.run')
    def test_clone_repository(self, mock_run):
        """Test cloning a repository."""
        # Mock successful subprocess run
        mock_run.return_value.stdout = "Cloning into 'test_dir'..."
        mock_run.return_value.stderr = ""
        
        # Test cloning
        result = self.git.clone_repository()
        self.assertTrue(result)
        
        # Verify git clone was called with correct arguments
        mock_run.assert_called_once()
        args = mock_run.call_args[0][0]
        self.assertEqual(args[0], "git")
        self.assertEqual(args[1], "clone")
        self.assertTrue(self.repo_url in args[2] or "test_user:test_token" in args[2])
        
    @patch('subprocess.run')
    def test_checkout_branch(self, mock_run):
        """Test checking out a branch."""
        # Mock successful subprocess run
        mock_run.return_value.stdout = "Switched to branch 'test-branch'"
        mock_run.return_value.stderr = ""
        
        # Test checkout
        result = self.git.checkout_branch("test-branch")
        self.assertTrue(result)
        
        # Verify git checkout was called with correct arguments
        mock_run.assert_called_once()
        args = mock_run.call_args[0][0]
        self.assertEqual(args[0], "git")
        self.assertEqual(args[1], "checkout")
        self.assertEqual(args[2], "test-branch")
        
    @patch('subprocess.run')
    def test_commit_changes(self, mock_run):
        """Test committing changes."""
        # Mock successful subprocess run for git add
        mock_run.return_value.stdout = ""
        mock_run.return_value.stderr = ""
        
        # Test commit
        result = self.git.commit_changes("Test commit message")
        self.assertTrue(result)
        
        # Verify git commit was called with correct arguments
        args = mock_run.call_args[0][0]
        self.assertEqual(args[0], "git")
        self.assertEqual(args[1], "commit")
        self.assertEqual(args[2], "-m")
        self.assertEqual(args[3], "Test commit message")
        
    def test_get_authenticated_url(self):
        """Test generating authenticated URL."""
        # Test with username and token
        auth_url = self.git._get_authenticated_url()
        self.assertIn("test_user:test_token", auth_url)
        
        # Test without credentials
        git_no_auth = GitIntegration(
            repo_url=self.repo_url,
            local_path=self.test_dir
        )
        auth_url = git_no_auth._get_authenticated_url()
        self.assertEqual(auth_url, self.repo_url)
        
    def test_update_file(self):
        """Test updating a file."""
        # Create a test file
        test_file = os.path.join(self.test_dir, "test.txt")
        os.makedirs(self.test_dir, exist_ok=True)
        
        # Update the file
        result = self.git.update_file("test.txt", "Test content")
        self.assertTrue(result)
        
        # Verify file was created with correct content
        with open(test_file, 'r') as f:
            content = f.read()
        self.assertEqual(content, "Test content")


class TestWebsiteUpdater(unittest.TestCase):
    """Test cases for the website updater module."""
    
    def setUp(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp()
        
        # Mock GitIntegration
        self.git = MagicMock()
        self.git.local_path = self.test_dir
        
        # Mock AnalyticsEngine
        self.analytics = MagicMock()
        
        # Create WebsiteUpdater
        self.updater = WebsiteUpdater(
            git_integration=self.git,
            analytics_engine=self.analytics
        )
        
    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.test_dir, ignore_errors=True)
        
    def test_prepare_repository(self):
        """Test preparing the repository."""
        # Mock successful git operations
        self.git.clone_repository.return_value = True
        self.git.pull_latest_changes.return_value = True
        
        # Test prepare repository
        result = self.updater.prepare_repository()
        self.assertTrue(result)
        
        # Verify git operations were called
        self.git.pull_latest_changes.assert_called_once()
        
    def test_create_update_branch(self):
        """Test creating an update branch."""
        # Mock successful git operation
        self.git.create_and_switch_branch.return_value = True
        
        # Test create update branch
        result = self.updater.create_update_branch()
        self.assertTrue(result)
        
        # Verify git operation was called
        self.git.create_and_switch_branch.assert_called_once()
        
    def test_update_content_based_on_analytics(self):
        """Test updating content based on analytics."""
        # Mock analytics data
        self.analytics.get_content_performance.return_value = {
            "items": [
                {
                    "file_path": "index.html",
                    "conversion_rate": 0.01,  # Below threshold
                    "issue": "conversion_rate"
                }
            ]
        }
        
        # Mock git operations
        self.git.get_file_content.return_value = "<html><body>Test</body></html>"
        self.git.update_file.return_value = True
        
        # Test update content
        updated_files = self.updater.update_content_based_on_analytics()
        
        # Verify file was updated
        self.assertEqual(len(updated_files), 1)
        self.assertEqual(updated_files[0], "index.html")
        
    def test_commit_and_push_changes(self):
        """Test committing and pushing changes."""
        # Mock git operations
        self.git.commit_changes.return_value = True
        self.git.push_changes.return_value = True
        
        # Enable auto commit and push
        self.updater.config["auto_commit"] = True
        self.updater.config["auto_push"] = True
        
        # Test commit and push
        result = self.updater.commit_and_push_changes(["index.html", "style.css"])
        self.assertTrue(result)
        
        # Verify git operations were called
        self.git.commit_changes.assert_called_once()
        self.git.push_changes.assert_called_once()
        
    def test_run_update_cycle(self):
        """Test running a complete update cycle."""
        # Mock all the methods
        self.updater.prepare_repository = MagicMock(return_value=True)
        self.updater.create_update_branch = MagicMock(return_value=True)
        self.updater.update_content_based_on_analytics = MagicMock(return_value=["index.html"])
        self.updater.update_meta_tags_based_on_seo = MagicMock(return_value=["about.html"])
        self.updater.commit_and_push_changes = MagicMock(return_value=True)
        
        # Test run update cycle
        result = self.updater.run_update_cycle()
        self.assertTrue(result)
        
        # Verify all methods were called
        self.updater.prepare_repository.assert_called_once()
        self.updater.create_update_branch.assert_called_once()
        self.updater.update_content_based_on_analytics.assert_called_once()
        self.updater.update_meta_tags_based_on_seo.assert_called_once()
        self.updater.commit_and_push_changes.assert_called_once_with(["index.html", "about.html"])


if __name__ == "__main__":
    unittest.main()

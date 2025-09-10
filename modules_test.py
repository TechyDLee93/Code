#############################################################################
# modules_test.py
#
# This file contains tests for modules.py.
#
# You will write these tests in Unit 2.
#############################################################################

import unittest
from unittest.mock import patch
from streamlit.testing.v1 import AppTest
from modules import display_post, display_activity_summary, display_genai_advice, display_recent_workouts

# Import for display_post
from unittest.mock import patch, MagicMock
import requests

# Write your tests below

class TestDisplayPost(unittest.TestCase):
    """Tests the display_post function."""

    @patch("modules.requests.get")
    def test_create_valid_post(self, mock_get):
        # Mock a successful image request
        mock_get.return_value.status_code = 200
        mock_get.return_value.headers = {'Content-Type': 'image/png'}

        # Valid input data
        username = "test_user"
        user_image = "https://example.com/user.png"
        timestamp = "2025-03-12 10:00:00"
        content = "This is a test post."
        post_image = "https://example.com/post.png"

        # Call the function
        display_post(username, user_image, timestamp, content, post_image)

        # Assertions (mocked request should have been called)
        mock_get.assert_called_with(post_image, stream=True, timeout=5)
    
    @patch('modules.requests.get')
    @patch('modules.st.warning')
    @patch('modules.st.session_state', new_callable=lambda: type('SessionStateMock', (object,), {})())
    @patch('modules.st.markdown')
    def test_display_post_invalid_image(self, mock_markdown, mock_session_state, mock_warning, mock_requests_get):
        """Test display_post with an invalid image URL."""
        mock_requests_get.side_effect = requests.RequestException("Error")

        display_post("TestUser", "invalid_url", "2025-03-12", "Test content", "invalid_url")

        mock_warning.assert_called_with("Invalid image URL. Please upload a valid image.")
        self.assertEqual(mock_session_state.post_image, "https://via.placeholder.com/600x400?text=No+Image")
        mock_markdown.assert_called()
    
    @patch('modules.st.markdown')
    def test_display_post_handles_none_values(self, mock_markdown):
        """Test display_post with None values."""
        display_post(None, None, None, None, None)
        mock_markdown.assert_called()

class TestDisplayActivitySummary(unittest.TestCase):
    """Tests the display_activity_summary function."""

    def test_foo(self):
        """Tests foo."""
        pass


class TestDisplayGenAiAdvice(unittest.TestCase):
    """Tests the display_genai_advice function."""
    #test that the app runs properly
    def test_app_runs(self):
        at = AppTest.from_file("app.py")
        at.run()
        assert not at.exception
    
    @patch("streamlit.image")
    def test_image_appears(self, mock_image):
        timestamp = "2024-01-01 00:00:00"
        content = "You're doing great! Keep up the good work." 
        image = "https://plus.unsplash.com/premium_photo-1669048780129-051d670fa2d1?q=80&w=3870&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D"

        #test that the image displays correctly
        display_genai_advice(timestamp, content, image)
        mock_image.assert_called_with(image)

class TestDisplayRecentWorkouts(unittest.TestCase):
    """Tests the display_recent_workouts function."""

    def test_foo(self):
        """Tests foo."""
        pass


if __name__ == "__main__":
    unittest.main()

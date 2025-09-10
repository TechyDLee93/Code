#############################################################################
# modules_test.py
#
# This file contains tests for modules.py.
#
# You will write these tests in Unit 2.
#############################################################################

import unittest
from unittest.mock import patch
import matplotlib.pyplot as plt
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
    
    #ChatGPT helped write the syntax for these tests 
    def test_function_runs_without_error(self):
        sample_workouts = [
        {"start_timestamp": "2025-03-01 08:00", "end_timestamp": "2025-03-01 09:00", "distance": 5, "steps": 6000, "calories_burned": 400},
        {"start_timestamp": "2025-03-02 08:30", "end_timestamp": "2025-03-02 09:15", "distance": 7.2, "steps": 8000, "calories_burned": 550},
        ]
        try:
            display_activity_summary(sample_workouts)
        except Exception as e:
            self.fail(f"Function raised an exception {e} unexpectedly!")

    @patch('streamlit.dataframe')
    @patch('streamlit.pyplot')
    def test_table_renders(self, mock_pyplot, mock_dataframe):
        """Test that the summary table is rendered using placeholders for the Streamlit environment"""
        sample_workouts = [
            {"start_timestamp": "2025-03-01 08:00", "end_timestamp": "2025-03-01 09:00", "distance": 5, "steps": 6000, "calories_burned": 400},
            {"start_timestamp": "2025-03-02 08:30", "end_timestamp": "2025-03-02 09:15", "distance": 7.2, "steps": 8000, "calories_burned": 550},
        ]
        display_activity_summary(sample_workouts)  
        mock_dataframe.assert_called_once()  # Ensure dataframe is called

    @patch('streamlit.dataframe')
    @patch('streamlit.pyplot')
    def test_graph_renders(self, mock_pyplot, mock_dataframe):
        """Test that the graph is rendered using placeholders for the Streamlit environment"""
        sample_workouts = [
            {"start_timestamp": "2025-03-01 08:00", "end_timestamp": "2025-03-01 09:00", "distance": 5, "steps": 6000, "calories_burned": 400},
            {"start_timestamp": "2025-03-02 08:30", "end_timestamp": "2025-03-02 09:15", "distance": 7.2, "steps": 8000, "calories_burned": 550},
        ]
        display_activity_summary(sample_workouts)
        mock_pyplot.assert_called_once()  # Ensure plot is called


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
    def test_empty_workouts_list(self):
        """Test when the workouts list is empty"""
        result = display_recent_workouts([])
        self.assertIsNone(result)  # Should return nothing

    def test_single_workout_entry(self):
        """Test when there is a single workout"""
        workouts = [{
            'workout_id': 'workout1',
            'start_timestamp': '2024-03-10 08:00:00',
            'end_timestamp': '2024-03-10 08:30:00',
            'start_lat_lng': 2.36,
            'end_lat_lng': 1.5444,
            'distance': 5.2,
            'steps': 6000,
            'calories_burned': 300
        }]
        result = display_recent_workouts(workouts)
        self.assertIsNone(result)

    def test_multiple_workouts_sorted(self):
        """Test multiple workouts sorted by timestamp"""
        workouts = [
            {'workout_id': 'workout1', 'start_timestamp': '2024-03-10 08:00:00', 'end_timestamp': '2024-03-10 08:30:00',
            'start_lat_lng': 2.0, 'end_lat_lng': 2.0, 'distance': 5.2, 'steps': 6000, 'calories_burned': 300},

            {'workout_id': 'workout2', 'start_timestamp': '2024-03-11 09:00:00', 'end_timestamp': '2024-03-11 09:45:00',
            'start_lat_lng': 2.0, 'end_lat_lng': 2.0, 'distance': 3.0, 'steps': 4000, 'calories_burned': 250}
        ]

        display_recent_workouts(workouts)
        self.assertEqual(workouts[0]['workout_id'], 'workout2')  # Most recent should be first
        self.assertEqual(workouts[1]['workout_id'], 'workout1')  # Older should be second

    def test_workouts_with_same_start_time(self):
        """Test multiple workouts with the same timestamp"""
        workouts = [
            {'workout_id': 'workout1', 'start_timestamp': '2024-03-11 09:00:00', 'end_timestamp': '2024-03-11 09:45:00',
            'start_lat_lng': 2.0, 'end_lat_lng': 2.0, 'distance': 3.0, 'steps': 4000, 'calories_burned': 250},

            {'workout_id': 'workout2', 'start_timestamp': '2024-03-11 09:00:00', 'end_timestamp': '2024-03-11 09:45:00',
            'start_lat_lng': 2.0, 'end_lat_lng': 2.0, 'distance': 4.0, 'steps': 5000, 'calories_burned': 300}
        ]

        display_recent_workouts(workouts)
        self.assertEqual(len(workouts), 2)  # Both workouts should be displayed
        self.assertEqual(workouts[0]['workout_id'], 'workout1')  # Order should be unchanged

    def test_workout_with_zero_and_negative_values(self):
        """Test workout with zero and negative values"""
        workouts = [
            {'workout_id': 'workout1', 'start_timestamp': '2024-03-10 07:00:00', 'end_timestamp': '2024-03-10 07:30:00',
            'start_lat_lng': 2.0, 'end_lat_lng': 2.0, 'distance': 0, 'steps': 0, 'calories_burned': -100}
        ]

        display_recent_workouts(workouts)
        self.assertEqual(workouts[0]['distance'], 0)
        self.assertEqual(workouts[0]['steps'], 0)
        self.assertEqual(workouts[0]['calories_burned'], -100)

    def test_large_number_of_workouts(self):
        """Test function with a large number of workouts"""
        workouts = []
        for i in range(100):
            workouts.append({
                'workout_id': f'workout{i}',
                'start_timestamp': f'2024-03-{10 + i} 07:00:00',
                'end_timestamp': f'2024-03-{10 + i} 07:30:00',
                'start_lat_lng': 2.0,
                'end_lat_lng': 2.0,
                'distance': 5.0,
                'steps': 6000,
                'calories_burned': 300
            })

        display_recent_workouts(workouts)
        self.assertEqual(len(workouts), 100)  # Ensure all workouts are processed

if __name__ == "__main__":
    unittest.main()

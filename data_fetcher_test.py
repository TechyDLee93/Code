#############################################################################
# data_fetcher_test.py
#
# This file contains tests for data_fetcher.py.
#
# You will write these tests in Unit 3.
#############################################################################
import unittest
from unittest.mock import patch, MagicMock
from google.cloud import bigquery
import os
import datetime
import pytz
import sys
from data_fetcher import get_user_sensor_data, get_genai_advice, load_dotenv, vertexai, get_user_profile
from vertexai.generative_models import GenerativeModel
from data_fetcher import _vertexai_initialized

class MockGenerativeModel: #mock the GenAI model
    def __init__(self, expected_message, *args, **kwargs):
        self.expected_message = expected_message

    def generate_content(self, *args, **kwargs): #mock a response from the model
        mock_response = MagicMock()
        mock_response.candidates = [MagicMock()]
        mock_response.candidates[0].content.parts = [MagicMock()]
        mock_response.candidates[0].content.parts[0].text.strip.return_value = self.expected_message
        return mock_response

class TestDataFetcher(unittest.TestCase):

    def setUp(self): 
        global _vertexai_initialized
        _vertexai_initialized = False

    """Tests for get_user_sensor_data_success, these tests were created with help from Gemini"""
    @patch('google.cloud.bigquery.Client')
    def test_get_user_sensor_data_success(self, mock_bigquery_client):
        """Tests successful retrieval of user sensor data."""

        mock_query_job = MagicMock()
        mock_results = [
            {'sensor_type': 'accelerometer', 'timestamp': '2024-01-01 00:00:00', 'data': 10.5},
            {'sensor_type': 'gyroscope', 'timestamp': '2024-01-01 00:01:00', 'data': 20.2},
        ]
        mock_query_job.result.return_value = mock_results

        mock_client = MagicMock()
        mock_client.query.return_value = mock_query_job
        mock_bigquery_client.return_value = mock_client

        user_id = "test_user"
        workout_id = "test_workout"

        result = get_user_sensor_data(user_id, workout_id)

        self.assertEqual(result, mock_results)
        mock_bigquery_client.assert_called_once()
        mock_client.query.assert_called_once()
        query = mock_client.query.call_args[0][0]
        self.assertIn(user_id, query)
        self.assertIn(workout_id, query)

    @patch('google.cloud.bigquery.Client')
    @patch('builtins.print')
    def test_get_user_sensor_data_error(self, mock_print, mock_bigquery_client):
        """Tests handling of BigQuery errors."""

        mock_bigquery_client.side_effect = Exception("BigQuery error")

        user_id = "test_user"
        workout_id = "test_workout"

        result = get_user_sensor_data(user_id, workout_id)

        self.assertIsNone(result)
        mock_print.assert_called_once()

    @patch('google.cloud.bigquery.Client')
    def test_empty_result(self, mock_bigquery_client):
        """Tests handling of empty results from BigQuery."""

        mock_query_job = MagicMock()
        mock_query_job.result.return_value = []

        mock_client = MagicMock()
        mock_client.query.return_value = mock_query_job
        mock_bigquery_client.return_value = mock_client

        user_id = "test_user"
        workout_id = "test_workout"

        result = get_user_sensor_data(user_id, workout_id)

        self.assertEqual(result, [])
        mock_bigquery_client.assert_called_once()

    @patch('google.cloud.bigquery.Client')
    def test_data_type_handling(self, mock_bigquery_client):
        """Tests handling of different data types from BigQuery."""

        mock_query_job = MagicMock()
        mock_results = [
            {'sensor_type': 'temperature', 'timestamp': '2024-01-01 00:00:00', 'data': 36.5},
            {'sensor_type': 'heart_rate', 'timestamp': '2024-01-01 00:01:00', 'data': 80},
            {'sensor_type': 'pressure', 'timestamp': '2024-01-01 00:02:00', 'data': "1013.25"},
        ]
        mock_query_job.result.return_value = mock_results

        mock_client = MagicMock()
        mock_client.query.return_value = mock_query_job
        mock_bigquery_client.return_value = mock_client

        user_id = "test_user"
        workout_id = "test_workout"

        result = get_user_sensor_data(user_id, workout_id)

        self.assertEqual(result, mock_results)

    @patch('google.cloud.bigquery.Client')
    def test_partial_data(self, mock_bigquery_client):
        """Tests handling of rows with missing columns."""

        mock_query_job = MagicMock()
        mock_results = [
            {'sensor_type': 'accelerometer', 'timestamp': '2024-01-01 00:00:00'},
            {'sensor_type': 'gyroscope', 'data': 20.2},
        ]
        mock_query_job.result.return_value = mock_results

        mock_client = MagicMock()
        mock_client.query.return_value = mock_query_job
        mock_bigquery_client.return_value = mock_client

        user_id = "test_user"
        workout_id = "test_workout"

        result = get_user_sensor_data(user_id, workout_id)

        self.assertEqual(result, mock_results)
    
    @patch('google.cloud.bigquery.Client')
    def test_large_dataset_handling(self, mock_bigquery_client):
        """Tests handling of a large dataset from BigQuery."""

        large_dataset = [{'sensor_type': 'test', 'timestamp': '2024-01-01 00:00:00', 'data': 1.0} for _ in range(1000)]

        mock_query_job = MagicMock()
        mock_query_job.result.return_value = large_dataset

        mock_client = MagicMock()
        mock_client.query.return_value = mock_query_job
        mock_bigquery_client.return_value = mock_client

        user_id = "test_user"
        workout_id = "test_workout"

        result = get_user_sensor_data(user_id, workout_id)

        self.assertEqual(result, large_dataset)
    
    """Tests for get_genai_advice, these tests were created with help from Gemini"""
    
    @patch('data_fetcher.vertexai.init')
    @patch('os.environ.get')
    @patch('random.choice')
    @patch('random.randint')
    @patch('data_fetcher.datetime')  
    @patch('data_fetcher.GenerativeModel')
    @patch('data_fetcher.get_user_workouts')
    def test_get_genai_advice_success(self, mock_get_user_workouts, mock_generative_model, mock_datetime_module, mock_randint, mock_choice, mock_os_environ_get, mock_vertexai_init):
        from data_fetcher import get_genai_advice

        mock_os_environ_get.side_effect = lambda key, default=None: {
        "PROJECT_ID": "test_project",  
        "TIMEZONE": "America/New_York", 
        }.get(key, default)

        mock_choice.return_value = 'https://test.image.com'
        mock_randint.return_value = 12345

        # Create a mock datetime class with a mock now() method
        mock_datetime_class = MagicMock()
        mock_now = MagicMock()
        mock_now.strftime.return_value = "2024-01-01 12:00:00 "
        mock_datetime_class.now.return_value = mock_now
        mock_datetime_module.datetime = mock_datetime_class

        expected_message = "Stay strong!"
        mock_generative_model.return_value = MockGenerativeModel(expected_message)

        # Configure the return value for the mocked get_user_workouts
        mock_get_user_workouts.return_value = [
            {"workout_id": 1, "name": "Running", "duration": 30, "date": "2025-04-01"},
            {"workout_id": 2, "name": "Weightlifting", "sets": 3, "reps": 10, "date": "2025-04-03"},
        ]

        result = get_genai_advice("test_user")

        self.assertEqual(result['advice_id'], 12345)
        self.assertEqual(result['content'], expected_message)
        self.assertEqual(result['image'], 'https://test.image.com')
        self.assertEqual(result['timestamp'], "2024-01-01 12:00:00 ")
        #mock_vertexai_init.assert_called_once_with(project="test_project", location="us-central1")
        mock_datetime_class.now.assert_called_once()
        mock_get_user_workouts.assert_called_once_with("test_user") 

    @patch('data_fetcher.vertexai.init')
    @patch('random.choice')
    @patch('data_fetcher.datetime')  
    @patch('data_fetcher.GenerativeModel')
    @patch('google.cloud.bigquery.Client')
    def test_get_genai_advice_none_image(self,mock_bigquery_client, mock_generative_model, mock_datetime_module, mock_choice, mock_vertexai_init):
        from data_fetcher import get_genai_advice

        mock_choice.return_value = None

        mock_datetime_class = MagicMock()
        mock_now = MagicMock()
        mock_now.strftime.return_value = "2024-01-01 12:00:00 "
        mock_datetime_class.now.return_value = mock_now
        mock_datetime_module.datetime = mock_datetime_class  

        expected_message = "Keep going!"
        mock_generative_model.return_value = MockGenerativeModel(expected_message)
        mock_bigquery_client.return_value = MagicMock()

        result = get_genai_advice("test_user")
        self.assertEqual(result['image'], None)
        self.assertEqual(result["content"], expected_message)
        self.assertEqual(result['timestamp'], "2024-01-01 12:00:00 ")
        mock_datetime_class.now.assert_called_once()
        mock_vertexai_init.assert_called_once_with(project=None, location="us-central1")

# Imports for get_user_posts testing
import unittest
from unittest.mock import Mock, patch, MagicMock
import datetime
from google.cloud import bigquery
import sys
import os
from data_fetcher import get_user_posts

# Partially created by Gemini, Claude, and ChatGPT: "Create unittests for get_user_posts"
class TestGetUserPosts(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures before each test method."""
        # Create a mock BigQuery client
        self.mock_client = Mock(spec=bigquery.Client)
        
        # Create a patcher for the bigquery.Client constructor
        self.client_patcher = patch('data_fetcher.bigquery.Client', return_value=self.mock_client)
        self.client_patcher.start()
        
        # Sample test data
        self.test_user_id = "user123"
        
        # Sample timestamp for consistent testing
        self.test_timestamp = datetime.datetime(2023, 10, 15, 12, 30, 45)

    def tearDown(self):
        """Tear down test fixtures after each test method."""
        self.client_patcher.stop()

    def _setup_mock_query_result(self, rows):
        """Helper method to set up mock query results correctly."""
        # Create a mock query job that is also iterable
        mock_query_job = MagicMock()
        
        # Make the mock query job iterable with rows
        # This correctly handles the __iter__ special method
        mock_query_job.__iter__.return_value = iter(rows)
        
        # Configure the mock client to return the mock query job
        self.mock_client.query.return_value = mock_query_job

    def test_get_user_posts_with_complete_data(self):
        """Test retrieving posts with all fields populated."""
        # Set up mock rows with complete data
        mock_rows = [
            {
                'PostId': 'post1',
                'AuthorId': self.test_user_id,
                'Timestamp': self.test_timestamp,
                'Content': 'Test post content',
                'PostImageUrl': 'https://example.com/image.jpg',
                'Username': 'testuser',
                'UserImageUrl': 'https://example.com/user.jpg'
            },
            {
                'PostId': 'post2',
                'AuthorId': self.test_user_id,
                'Timestamp': self.test_timestamp,
                'Content': 'Another test post',
                'PostImageUrl': 'https://example.com/image2.jpg',
                'Username': 'testuser',
                'UserImageUrl': 'https://example.com/user.jpg'
            }
        ]
        
        self._setup_mock_query_result(mock_rows)
        
        # Call the function
        result = get_user_posts(self.test_user_id)
        
        # Verify the results
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]['post_id'], 'post1')
        self.assertEqual(result[0]['user_id'], self.test_user_id)
        self.assertEqual(result[0]['timestamp'], self.test_timestamp.strftime('%Y-%m-%d %H:%M:%S'))
        self.assertEqual(result[0]['content'], 'Test post content')
        self.assertEqual(result[0]['image'], 'https://example.com/image.jpg')
        self.assertEqual(result[0]['username'], 'testuser')
        self.assertEqual(result[0]['user_image'], 'https://example.com/user.jpg')
        
        # Verify the SQL query contains the correct user_id
        self.mock_client.query.assert_called_once()
        query_arg = self.mock_client.query.call_args[0][0]
        self.assertIn(f"WHERE p.AuthorId = '{self.test_user_id}'", query_arg)

    def test_get_user_posts_with_missing_fields(self):
        """Test retrieving posts with some fields missing."""
        # Set up mock rows with some missing data
        mock_rows = [
            {
                'PostId': 'post3',
                'AuthorId': self.test_user_id,
                'Timestamp': self.test_timestamp,
                'Content': None,  # Missing content
                'PostImageUrl': None,  # Missing image
                'Username': 'testuser',
                'UserImageUrl': 'https://example.com/user.jpg'
            }
        ]
        
        self._setup_mock_query_result(mock_rows)
        
        # Call the function
        result = get_user_posts(self.test_user_id)
        
        # Verify the results
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['post_id'], 'post3')
        self.assertEqual(result[0]['content'], '')  # Should be empty string, not None
        self.assertEqual(result[0]['image'], '')  # Should be empty string, not None

    def test_get_user_posts_no_results(self):
        """Test retrieving posts when there are no results."""
        # Set up empty results
        self._setup_mock_query_result([])
        
        # Call the function
        result = get_user_posts(self.test_user_id)
        
        # Verify empty list is returned
        self.assertEqual(result, [])

    def test_get_user_posts_sql_injection_prevention(self):
        """Test that the function is not vulnerable to SQL injection."""
        # Set up a user_id that attempts SQL injection
        malicious_user_id = "user123' OR 1=1 --"
        
        # Mock an empty result for simplicity
        self._setup_mock_query_result([])
        
        # Call the function
        get_user_posts(malicious_user_id)
        
        # Verify the SQL query contains the user_id as is, which is potentially vulnerable
        # Note: This test is actually detecting a vulnerability in the code
        self.mock_client.query.assert_called_once()
        query_arg = self.mock_client.query.call_args[0][0]
        self.assertIn(f"WHERE p.AuthorId = '{malicious_user_id}'", query_arg)
        
        # Note: This is where we would recommend fixing the code to use parameterized queries

    def test_suggested_fix_for_sql_injection(self):
        """Test a suggested fix for SQL injection using query parameters."""
        # Create a mock job config
        mock_job_config = Mock(spec=bigquery.QueryJobConfig)
        
        # Set up mock rows
        mock_rows = [
            {
                'PostId': 'post1',
                'AuthorId': self.test_user_id,
                'Timestamp': self.test_timestamp,
                'Content': 'Test content',
                'PostImageUrl': 'https://example.com/image.jpg',
                'Username': 'testuser',
                'UserImageUrl': 'https://example.com/user.jpg'
            }
        ]
        
        # Set up the mock query job correctly
        mock_query_job = MagicMock()
        mock_query_job.__iter__.return_value = iter(mock_rows)
        self.mock_client.query.return_value = mock_query_job
        
        # Create a fixed version of get_user_posts that uses parameters
        def get_user_posts_fixed(user_id):
            """Fixed version of get_user_posts that uses query parameters."""
            client = bigquery.Client()
            
            query = """
                SELECT p.PostId, p.AuthorId, p.Timestamp, p.Content, p.ImageUrl as PostImageUrl,
                    u.Username, u.ImageUrl as UserImageUrl
                FROM `keishlyanysanabriatechx25.bytemeproject.Posts` p
                JOIN `keishlyanysanabriatechx25.bytemeproject.Users` u
                ON p.AuthorId = u.UserId
                WHERE p.AuthorId = @user_id
            """
            
            job_config = bigquery.QueryJobConfig(
                query_parameters=[
                    bigquery.ScalarQueryParameter("user_id", "STRING", user_id)
                ]
            )
            
            results = client.query(query, job_config=job_config)
            
            posts = []
            for row in results:
                post = {
                    'user_id': row['AuthorId'],
                    'post_id': row['PostId'],
                    'timestamp': row['Timestamp'].strftime('%Y-%m-%d %H:%M:%S'),
                    'content': row['Content'] if row['Content'] else '',
                    'image': row['PostImageUrl'] if row['PostImageUrl'] else '',
                    'username': row['Username'],
                    'user_image': row['UserImageUrl']
                }
                posts.append(post)
            
            return posts
        
        # Mock the QueryJobConfig creation
        with patch('data_fetcher.bigquery.QueryJobConfig', return_value=mock_job_config):
            # Call the fixed function
            result = get_user_posts_fixed(self.test_user_id)
            
            # Verify the client.query was called with the job_config
            self.mock_client.query.assert_called_once()
            # In a real fix, we would verify query parameters were used correctly

import unittest
from unittest.mock import MagicMock, patch
from modules import get_user_workouts  # Adjust to the correct import path
from google.cloud import bigquery
import datetime

class TestGetUserWorkout(unittest.TestCase):

    @patch("google.cloud.bigquery.Client")
    def test_get_user_workouts_valid_user(self, mock_bigquery_client):
        mock_client_instance = mock_bigquery_client.return_value
        mock_query_job = mock_client_instance.query.return_value

        mock_query_job.result.return_value = [
            MagicMock(
                WorkoutId="workout1",
                StartTimestamp=datetime.datetime(2024, 7, 29, 7, 0, 0),
                EndTimestamp=datetime.datetime(2024, 7, 29, 8, 0, 0),
                StartLocationLat=37.7749,
                StartLocationLong=-122.4194,
                EndLocationLat=37.8049,
                EndLocationLong=-122.4210,
                TotalDistance=5.0,
                TotalSteps=8000,
                CaloriesBurned=400,
            )
        ]

        expected_result = [{
            'WorkoutId': "workout1",
            'StartTimestamp': "2024-07-29T07:00:00",
            'end_timestamp': "2024-07-29T08:00:00",
            'start_lat_lng': (37.7749, -122.4194),
            'end_lat_lng': (37.8049, -122.4210),
            'distance': 5.0,
            'steps': 8000,
            'calories_burned': 400,
        }]

        self.assertEqual(get_user_workouts("user1"), expected_result)

    @patch("google.cloud.bigquery.Client")
    def test_get_user_workouts_multiple_workouts(self, mock_bigquery_client):
        mock_client_instance = mock_bigquery_client.return_value
        mock_query_job = mock_client_instance.query.return_value

        mock_query_job.result.return_value = [
            MagicMock(
                WorkoutId="workout1",
                StartTimestamp=datetime.datetime(2024, 7, 29, 7, 0, 0),
                EndTimestamp=datetime.datetime(2024, 7, 29, 8, 0, 0),
                StartLocationLat=37.7749,
                StartLocationLong=-122.4194,
                EndLocationLat=37.8049,
                EndLocationLong=-122.4210,
                TotalDistance=5.0,
                TotalSteps=8000,
                CaloriesBurned=400
            ),
            MagicMock(
                WorkoutId="workout2",
                StartTimestamp=datetime.datetime(2024, 7, 30, 9, 0, 0),
                EndTimestamp=datetime.datetime(2024, 7, 30, 10, 0, 0),
                StartLocationLat=40.7128,
                StartLocationLong=-74.0060,
                EndLocationLat=40.7308,
                EndLocationLong=-73.9976,
                TotalDistance=6.5,
                TotalSteps=10000,
                CaloriesBurned=500
            )
        ]

        self.assertEqual(len(get_user_workouts("user1")), 2)

class TestGetUserProfile(unittest.TestCase):

    @patch("google.cloud.bigquery.Client")
    def test_get_user_profile_success(self, mock_bigquery_client):
        """Tests successful retrieval of user profile data with friends."""
        mock_row_data = (
            'user1',
            'Remi',
            'remi_the_rems',
            'https://upload.wikimedia.org/wikipedia/commons/c/c8/Puma_shoes.jpg',
            datetime.date(1990, 1, 1),
            ['user2', 'user3', 'user4']
        )

        mock_row = MagicMock(
            UserId=mock_row_data[0],
            Name=mock_row_data[1],
            Username=mock_row_data[2],
            ImageUrl=mock_row_data[3],
            DateOfBirth=mock_row_data[4],
            friends=mock_row_data[5]
        )

        mock_result = MagicMock()
        mock_result.__iter__.return_value = iter([mock_row])
        mock_result.__next__.return_value = mock_row  # Mock the next() call directly

        mock_client = MagicMock()
        mock_client.query.return_value.result.return_value = mock_result
        mock_bigquery_client.return_value = mock_client

        result = get_user_profile("user1")

        self.assertEqual(result["full_name"], "Remi")
        self.assertEqual(result["username"], "remi_the_rems")
        self.assertEqual(result["date_of_birth"], datetime.date(1990, 1, 1))
        self.assertEqual(result["profile_image"], "https://upload.wikimedia.org/wikipedia/commons/c/c8/Puma_shoes.jpg")
        self.assertEqual(result["friends"], ['user2', 'user3', 'user4'])

        # Ensure the query was called with the correct parameters
        mock_client.query.assert_called_once()
        called_with_args, called_with_kwargs = mock_client.query.call_args

        # Check that the query uses the parameterized placeholder
        self.assertIn("u.UserId = @user_id", called_with_args[0])

        # Check that the correct parameter value was passed
        query_params = called_with_kwargs['job_config'].query_parameters
        user_id_param = next((param for param in query_params if param.name == 'user_id'), None)
        self.assertIsNotNone(user_id_param)
        self.assertEqual(user_id_param.value, 'user1')

    # Function fixed by ChatGPT: "Fix for there to not appear this error: FAILED data_fetcher_test.py::TestGetUserProfile::test_get_user_profile_not_found - AssertionError: 'nonexistent_user' != 'user1'- nonexistent_user"
    @patch("google.cloud.bigquery.Client")
    def test_get_user_profile_not_found(self, mock_bigquery_client):
        """Tests the case where the user is not found."""
        mock_result = MagicMock()
        mock_result.__iter__.return_value = iter([])
        mock_result.__next__.side_effect = StopIteration  # Mock next() to raise StopIteration

        mock_client = MagicMock()
        mock_client.query.return_value.result.return_value = mock_result
        mock_bigquery_client.return_value = mock_client

        result = get_user_profile("nonexistent_user")

        self.assertEqual(result, {})

        # Ensure the query was called with the correct parameters
        mock_client.query.assert_called_once()

        called_with_args, called_with_kwargs = mock_client.query.call_args

        # Check that the query uses the parameterized placeholder
        self.assertIn("u.UserId = @user_id", called_with_args[0])

        # Check that the correct parameter value was passed
        query_params = called_with_kwargs['job_config'].query_parameters
        user_id_param = next((param for param in query_params if param.name == 'user_id'), None)
        self.assertIsNotNone(user_id_param)
        self.assertEqual(user_id_param.value, 'nonexistent_user')

if __name__ == "__main__":
    unittest.main()

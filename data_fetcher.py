#############################################################################
# data_fetcher.py
#
# This file contains functions to fetch data needed for the app.
#
# You will re-write these functions in Unit 3, and are welcome to alter the
# data returned in the meantime. We will replace this file with other data when
# testing earlier units.
#############################################################################

import random
from google.cloud import bigquery
import os
import vertexai
from vertexai.generative_models import GenerativeModel
from dotenv import load_dotenv
import datetime
import pytz

_vertexai_initialized = False

# Import for get_user_posts
from google.cloud import bigquery

users = {
    'user1': {
        'full_name': 'Remi',
        'username': 'remi_the_rems',
        'date_of_birth': '1990-01-01',
        'profile_image': 'https://upload.wikimedia.org/wikipedia/commons/c/c8/Puma_shoes.jpg',
        'friends': ['user2', 'user3', 'user4'],
    },
    'user2': {
        'full_name': 'Blake',
        'username': 'blake',
        'date_of_birth': '1990-01-01',
        'profile_image': 'https://upload.wikimedia.org/wikipedia/commons/c/c8/Puma_shoes.jpg',
        'friends': ['user1'],
    },
    'user3': {
        'full_name': 'Jordan',
        'username': 'jordanjordanjordan',
        'date_of_birth': '1990-01-01',
        'profile_image': 'https://upload.wikimedia.org/wikipedia/commons/c/c8/Puma_shoes.jpg',
        'friends': ['user1', 'user4'],
    },
    'user4': {
        'full_name': 'Gemmy',
        'username': 'gems',
        'date_of_birth': '1990-01-01',
        'profile_image': 'https://upload.wikimedia.org/wikipedia/commons/c/c8/Puma_shoes.jpg',
        'friends': ['user1', 'user3'],
    },
}


def get_user_sensor_data(user_id, workout_id):

    '''Fetches data from BigQuery using a given SQL query.

    Args:
        query_string: The SQL query to execute.
        project_id: The Google Cloud project ID.

    Returns:
        A list of rows, where each row is a dictionary, or None if an error occurs.
    '''
    try:
        # Basic sanitization to prevent simple SQL injection
        '''user_id = re.sub(r"[^a-zA-Z0-9_ -]", "", user_id)
        workout_id = re.sub(r"[^a-zA-Z0-9_ -]", "", workout_id)'''
        client = bigquery.Client(project="keishlyanysanabriatechx25")

        query_string = f"""
            SELECT
            Workouts.UserId,
            COALESCE(SensorTypes.SensorId, SensorData.SensorId) AS SensorId,
            SensorTypes.Name,
            SensorTypes.Units,
            SensorData.Timestamp,
            SensorData.SensorValue
        FROM
            `keishlyanysanabriatechx25.bytemeproject.Workouts` AS Workouts
        INNER JOIN
            `keishlyanysanabriatechx25.bytemeproject.SensorData` AS SensorData
        ON Workouts.WorkoutId = SensorData.WorkoutID
        LEFT JOIN
            `keishlyanysanabriatechx25.bytemeproject.SensorTypes` AS SensorTypes
        ON SensorData.SensorId = SensorTypes.SensorId
        WHERE
        Workouts.UserId = '{user_id}'
        AND Workouts.WorkoutId = '{workout_id}';
        """

        query_job = client.query(query_string)
        results = query_job.result()

        data = [dict(row.items()) for row in results]
        return data

    except Exception as e:
        print(f"Error fetching BigQuery data: {e}")
        return None


def get_user_workouts(user_id):
    client = bigquery.Client()
    #print(f"Executing query for UserId: {user_id}")
    query = f"""
        SELECT
            WorkoutId,
            StartTimestamp,
            EndTimestamp,
            StartLocationLat,
            StartLocationLong,
            EndLocationLat,
            EndLocationLong,
            TotalDistance,
            TotalSteps,
            CaloriesBurned
        FROM
            `keishlyanysanabriatechx25.bytemeproject.Workouts`
        WHERE
            UserId = '{user_id}'
    """
    query_job = client.query(query)
    #print(f"Query job ID: {query_job.job_id}") # Useful for BigQuery job monitoring
    results = query_job.result()
    workouts = []
    for row in results:
        workouts.append({
            'WorkoutId': row.WorkoutId,
            'StartTimestamp': row.StartTimestamp.isoformat() if row.StartTimestamp else None,
            'end_timestamp': row.EndTimestamp.isoformat() if row.EndTimestamp else None,
            'start_lat_lng': (row.StartLocationLat, row.StartLocationLong) if row.StartLocationLat is not None and row.StartLocationLong is not None else None,
            'end_lat_lng': (row.EndLocationLat, row.EndLocationLong) if row.EndLocationLat is not None and row.EndLocationLong is not None else None,
            'distance': row.TotalDistance,
            'steps': row.TotalSteps,
            'calories_burned': row.CaloriesBurned,
        })
    #print(f"Number of workouts returned: {len(workouts)}")
    #print(workouts)
    return workouts


def get_user_profile(user_id):
    """Returns information about the given user.

    This function currently returns random data. You will re-write it in Unit 3.
    """
    if user_id not in users:
        raise ValueError(f'User {user_id} not found.')
    return users[user_id]

'''
Funcion partially created by ChatGPT and Claude: "fix the following Function: get_user_posts in data_fetcher.py 
Returns a list of a user's posts. Some data in a post may not be populated.
Input: user_id
Output: A list of posts. Each post is a dictionary with keys user_id, post_id, timestamp, content, and image." 
'''
def get_user_posts(user_id):
    """Returns a list of a user's posts from the BigQuery database.

    Args:
        user_id (str): The ID of the user whose posts are being fetched.

    Returns:
        list: A list of dictionaries, each representing a post with keys:
            'user_id', 'post_id', 'timestamp', 'content', 'image', 'username', and 'user_image'.
    """
    # Initialize a BigQuery client
    client = bigquery.Client()

    # Query to fetch posts for the given user_id and join with Users table
    query = f"""
        SELECT p.PostId, p.AuthorId, p.Timestamp, p.Content, p.ImageUrl as PostImageUrl,
            u.Username, u.ImageUrl as UserImageUrl
        FROM `keishlyanysanabriatechx25.bytemeproject.Posts` p
        JOIN `keishlyanysanabriatechx25.bytemeproject.Users` u
        ON p.AuthorId = u.UserId
        WHERE p.AuthorId = '{user_id}'
    """
    
    # Set up query parameters
    # job_config = bigquery.QueryJobConfig(
    #     query_parameters=[bigquery.ScalarQueryParameter("user_id", "STRING", user_id)]
    # )
    
    # Execute the query
    results = client.query(query)

    # Process the results and return the list of posts
    posts = []
    for row in results:
        post = {
            'user_id': row['AuthorId'],
            'post_id': row['PostId'],
            'timestamp': row['Timestamp'].strftime('%Y-%m-%d %H:%M:%S'),
            'content': row['Content'] if row['Content'] else '',  # Handle empty content
            'image': row['PostImageUrl'] if row['PostImageUrl'] else '',  # Handle missing post image
            'username': row['Username'],  # Add username from Users table
            'user_image': row['UserImageUrl']  # Add user's profile image from Users table
        }
        posts.append(post)
    
    return posts

def get_genai_advice(user_id):

    '''load_dotenv()

    vertexai.init(project=os.environ.get("dagutierrez17techx25"), location="us-central1")'''

    global _vertexai_initialized
    load_dotenv()
    if not _vertexai_initialized:
        import vertexai
        vertexai.init(project=os.environ.get("dagutierrez17techx25"), location="us-central1")
        _vertexai_initialized = True

    workouts = get_user_workouts(user_id)

    model = GenerativeModel("gemini-1.5-flash-002")

    system_instruction = ("You are a the main motivational trainer for a fitness app. You are getting information about the user's past workouts in the 'workouts' list of dictionaries")

    response = model.generate_content("Please give me a motivational message for the user of this fitness app based on the 'workouts' lis of dictionaries that is received by calling 'get_user_workouts'. Please just output 1 motivational message, and also please don't mention 'get_user_workouts', just say the message")
    
    image = random.choice([
        'https://plus.unsplash.com/premium_photo-1669048780129-051d670fa2d1?q=80&w=3870&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D',
        'https://joggo.run/blog/app/uploads/2022/01/running-inspiration-660x440.jpg.webp',
        'https://st4.depositphotos.com/2760050/21096/i/450/depositphotos_210961042-stock-photo-never-stop-silhouette-man-motion.jpg',
        None,
    ])

    id = random.randint(1, 10000)
    #advice_timestamp = datetime.datetime.now()
    timezone_name = 'America/New_York' # Example: Replace with your desired timezone
    timezone = pytz.timezone(timezone_name)
    now_in_timezone = datetime.datetime.now(timezone)
    advice_timestamp = now_in_timezone.strftime("%Y-%m-%d %H:%M:%S ")

    return {'advice_id': id, 'timestamp': advice_timestamp, 'content' : response.candidates[0].content.parts[0].text.strip(), 'image' : image}


   

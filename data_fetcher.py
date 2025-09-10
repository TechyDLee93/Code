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
    """Returns a list of timestampped information for a given workout.

    This function currently returns random data. You will re-write it in Unit 3.
    """
    sensor_data = []
    sensor_types = [
        'accelerometer',
        'gyroscope',
        'pressure',
        'temperature',
        'heart_rate',
    ]
    for index in range(random.randint(5, 100)):
        random_minute = str(random.randint(0, 59))
        if len(random_minute) == 1:
            random_minute = '0' + random_minute
        timestamp = '2024-01-01 00:' + random_minute + ':00'
        data = random.random() * 100
        sensor_type = random.choice(sensor_types)
        sensor_data.append(
            {'sensor_type': sensor_type, 'timestamp': timestamp, 'data': data}
        )
    return sensor_data


def get_user_workouts(user_id):
    """Returns a list of user's workouts.

    This function currently returns random data. You will re-write it in Unit 3.
    """
    workouts = []
    for index in range(random.randint(1, 3)):
        random_lat_lng_1 = (
            1 + random.randint(0, 100) / 100,
            4 + random.randint(0, 100) / 100,
        )
        random_lat_lng_2 = (
            1 + random.randint(0, 100) / 100,
            4 + random.randint(0, 100) / 100,
        )
        workouts.append({
            'workout_id': f'workout{index}',
            'start_timestamp': '2024-01-01 00:00:00',
            'end_timestamp': '2024-01-01 00:30:00',
            'start_lat_lng': random_lat_lng_1,
            'end_lat_lng': random_lat_lng_2,
            'distance': random.randint(0, 200) / 10.0,
            'steps': random.randint(0, 20000),
            'calories_burned': random.randint(0, 100),
        })
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
    """Returns the most recent advice from the genai model.

    This function currently returns random data. You will re-write it in Unit 3.
    """
    advice = random.choice([
        'Your heart rate indicates you can push yourself further. You got this!',
        "You're doing great! Keep up the good work.",
        'You worked hard yesterday, take it easy today.',
        'You have burned 100 calories so far today!',
    ])
    image = random.choice([
        'https://plus.unsplash.com/premium_photo-1669048780129-051d670fa2d1?q=80&w=3870&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D'#,
        #None,
    ])
    return {
        'advice_id': 'advice1',
        'timestamp': '2024-01-01 00:00:00',
        'content': advice,
        'image': image,
    }

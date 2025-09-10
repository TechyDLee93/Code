#############################################################################
# data_fetcher.py
#
# This file contains functions to fetch data needed for the app.
#
# You will re-write these functions in Unit 3, and are welcome to alter the
# data returned in the meantime. We will replace this file with other data when
# testing earlier units.
#############################################################################

import json
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

#asked Gemini for help on how to write the query since it needed a lot of parameters
def get_user_sensor_data(user_id, workout_id, client=None):
    if client is None:
        client = bigquery.Client(project="keishlyanysanabriatechx25")

    '''Fetches data from BigQuery using a given SQL query.

    Args:
        query_string: The SQL query to execute.
        project_id: The Google Cloud project ID.

    Returns:
        A list of rows, where each row is a dictionary, or None if an error occurs.
    '''
    try:
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

def get_user_workouts(user_id, client=None):
    if client is None:
        client = bigquery.Client()
    
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

# Function fixed by Claude: "Fix code so that it has job_config"
def get_user_profile(user_id, client=None):
    # function: get_user_profile
    # input: user_id (str) - the ID of the user whose profile is being fetched
    # output: dict - contains full_name, username, date_of_birth, profile_image, and friends list

    if client is None:
        client = bigquery.Client(project="keishlyanysanabriatechx25")
    
    query = """
        SELECT
    u.UserId,
    u.Name,
    u.Username,
    u.ImageUrl,
    u.DateOfBirth,
    ARRAY_AGG(CASE
        WHEN f.UserId1 = u.UserId THEN f.UserId2
        WHEN f.UserId2 = u.UserId THEN f.UserId1
        ELSE NULL
    END IGNORE NULLS) AS friends
    FROM
    keishlyanysanabriatechx25.bytemeproject.Users u
    LEFT JOIN
    keishlyanysanabriatechx25.bytemeproject.Friends f ON u.UserId = f.UserId1 OR u.UserId = f.UserId2
    WHERE
    u.UserId = @user_id
    GROUP BY
    u.UserId, u.Name, u.Username, u.ImageUrl, u.DateOfBirth
    """
    
    job_config = bigquery.QueryJobConfig(
        query_parameters=[bigquery.ScalarQueryParameter("user_id", "STRING", user_id)]
    )
    
    # Pass the job_config to the query method
    result = client.query(query, job_config=job_config).result()
    
    row = next(result, None)
    if row:
        return {
            "full_name": row.Name,
            "username": row.Username,
            "date_of_birth": row.DateOfBirth,
            "profile_image": row.ImageUrl,
            "friends": row.friends
        }
    else:
        return {}

'''
Funcion partially created by ChatGPT and Claude: "fix the following Function: get_user_posts in data_fetcher.py 
Returns a list of a user's posts. Some data in a post may not be populated.
Input: user_id
Output: A list of posts. Each post is a dictionary with keys user_id, post_id, timestamp, content, and image." 
'''
def get_user_posts(user_id, client=None):
    """Returns a list of a user's posts from the BigQuery database.

    Args:
        user_id (str): The ID of the user whose posts are being fetched.

    Returns:
        list: A list of dictionaries, each representing a post with keys:
            'user_id', 'post_id', 'timestamp', 'content', 'image', 'username', and 'user_image'.
    """

    if client is None:
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

'''
Function created by Claude AI: "create a function that adds by using these lines, it adds the post to the database:
post_content = f"I've taken {total_steps} steps in my fitness journey! #FitnessGoals" add_post_to_database(userId, post_content)"
'''
def add_post_to_database(user_id, content, image_url=None, client=None):
    """Adds a post to the BigQuery database.
   
    Args:
        user_id (str): The ID of the user creating the post.
        content (str): The content of the post.
        image_url (str, optional): URL of the image for the post. Defaults to None.
       
    Returns:
        bool: True if successful, False otherwise.
    """

    if client is None:
        client = bigquery.Client()

    try:
        # Generate a unique post ID (you might have a different approach)
        import uuid
        post_id = str(uuid.uuid4())
       
        # Get current timestamp
        from datetime import datetime
        current_timestamp = datetime.now()
       
        # Prepare the INSERT query
        table_id = "keishlyanysanabriatechx25.bytemeproject.Posts"
       
        # Prepare the row to be inserted
        rows_to_insert = [{
            'PostId': post_id,
            'AuthorId': user_id,
            'Timestamp': current_timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            'Content': content,
            'ImageUrl': image_url,
        }]
       
        # Insert the row into BigQuery
        errors = client.insert_rows_json(table_id, rows_to_insert)
       
        if errors == []:
            print(f"New post added successfully")
            return True
        else:
            print(f"Errors occurred while adding post: {errors}")
            return False
           
    except Exception as e:
        print(f"Error adding post to database: {e}")
        return False

def get_genai_advice(user_id):

    #had to do this global vertexai variable to handle mocks in tests correctly
    global _vertexai_initialized
    load_dotenv()
    if not _vertexai_initialized:
        import vertexai
        vertexai.init(project=os.environ.get("dagutierrez17techx25"), location="us-central1")
        _vertexai_initialized = True

    workouts = get_user_workouts(user_id)

    #call Gemini and give it instructions on how to answer
    model = GenerativeModel("gemini-1.5-flash-002")

    system_instruction = ("You are a the main motivational trainer for a fitness app. You are getting information about the user's past workouts in the 'workouts' list of dictionaries")

    response = model.generate_content("Please give me a motivational message for the user of this fitness app based on the 'workouts' lis of dictionaries that is received by calling 'get_user_workouts'. Please just output 1 motivational message, and also please don't mention 'get_user_workouts', just say the message")
    
    #added more possible images and randomly select 1
    image = random.choice([
        'https://plus.unsplash.com/premium_photo-1669048780129-051d670fa2d1?q=80&w=3870&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D',
        'https://joggo.run/blog/app/uploads/2022/01/running-inspiration-660x440.jpg.webp',
        'https://st4.depositphotos.com/2760050/21096/i/450/depositphotos_210961042-stock-photo-never-stop-silhouette-man-motion.jpg',
        None,
    ])

    id = random.randint(1, 10000) #create a random id for the advice
    timezone_name = 'America/New_York'  #get this timezone to display current time
    timezone = pytz.timezone(timezone_name)
    now_in_timezone = datetime.datetime.now(timezone)
    advice_timestamp = now_in_timezone.strftime("%Y-%m-%d %H:%M:%S ")

    return {'advice_id': id, 'timestamp': advice_timestamp, 'content' : response.candidates[0].content.parts[0].text.strip(), 'image' : image}

# Created by ChatGPT to "make a function that checks if the username is a friend of user_id and if that friend exists in the database"
def get_friend_data(user_id, friend_username, client=None):
    """
    Checks if the username exists, and if it's a valid friend (not yourself),
    determines if the two users are friends.
    """

    if client is None:
        client = bigquery.Client()

    # Step 1: Look up UserId of friend_username
    get_friend_id_query = """
    SELECT UserId FROM `keishlyanysanabriatechx25.bytemeproject.Users`
    WHERE Username = @friend_username
    """
    job_config_lookup = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("friend_username", "STRING", friend_username),
        ]
    )

    result = client.query(get_friend_id_query, job_config=job_config_lookup).result()
    rows = list(result)

    if not rows:
        return f"Username '{friend_username}' does not exist."

    friend_id = rows[0]["UserId"]

    # Step 2: Check for self
    if user_id == friend_id:
        return "You cannot add yourself as a friend."

    # Step 3: Check if the users are already friends
    check_friend_query = """
    SELECT * FROM `keishlyanysanabriatechx25.bytemeproject.Friends`
    WHERE (UserId1 = @user_id AND UserId2 = @friend_id)
       OR (UserId1 = @friend_id AND UserId2 = @user_id)
    """
    job_config_check = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("user_id", "STRING", user_id),
            bigquery.ScalarQueryParameter("friend_id", "STRING", friend_id),
        ]
    )

    friendship_result = client.query(check_friend_query, job_config=job_config_check).result()

    if friendship_result.total_rows > 0:
        return f"You and '{friend_username}' are friends."
    else:
        return f"You and '{friend_username}' are not friends yet."

# Function mostly made by ChatGPT: "Following the database structure, create a function that lets the user send a friend request"
def send_friend_request(user_id, friend_username, client=None):
    """
    Sends a friend request from user_id to the user with friend_username.
    """

    if client is None:
        client = bigquery.Client()

    # Step 1: Resolve friend_username to friend_id
    get_friend_id_query = """
    SELECT UserId FROM `keishlyanysanabriatechx25.bytemeproject.Users`
    WHERE Username = @friend_username
    """
    job_config_lookup = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("friend_username", "STRING", friend_username),
        ]
    )

    result = client.query(get_friend_id_query, job_config=job_config_lookup).result()
    rows = list(result)

    if not rows:
        return f"Username '{friend_username}' does not exist."

    friend_id = rows[0]["UserId"]

    # Step 2: Prevent sending to self
    if friend_id == user_id:
        return "You cannot send a friend request to yourself."

    # Step 3: Check if they're already friends
    check_friend_query = """
    SELECT * FROM `keishlyanysanabriatechx25.bytemeproject.Friends`
    WHERE (UserId1 = @user_id AND UserId2 = @friend_id)
       OR (UserId1 = @friend_id AND UserId2 = @user_id)
    """
    job_config_check = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("user_id", "STRING", user_id),
            bigquery.ScalarQueryParameter("friend_id", "STRING", friend_id),
        ]
    )

    if client.query(check_friend_query, job_config=job_config_check).result().total_rows > 0:
        return f"You are already friends with {friend_username}."

    # Step 4: Check if a request already exists
    check_request_query = """
    SELECT * FROM `keishlyanysanabriatechx25.bytemeproject.FriendRequests`
    WHERE (RequesterId = @user_id AND ReceiverId = @friend_id)
       OR (RequesterId = @friend_id AND ReceiverId = @user_id)
    """
    job_config_request_check = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("user_id", "STRING", user_id),
            bigquery.ScalarQueryParameter("friend_id", "STRING", friend_id),
        ]
    )

    if client.query(check_request_query, job_config=job_config_request_check).result().total_rows > 0:
        return f"A friend request is already pending between you and {friend_username}."

    # Step 5: Insert the friend request
    insert_request_query = """
    INSERT INTO `keishlyanysanabriatechx25.bytemeproject.FriendRequests` (RequesterId, ReceiverId, RequestedAt)
    VALUES (@user_id, @friend_id, CURRENT_TIMESTAMP())
    """
    job_config_insert = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("user_id", "STRING", user_id),
            bigquery.ScalarQueryParameter("friend_id", "STRING", friend_id),
        ]
    )

    client.query(insert_request_query, job_config=job_config_insert).result()
    return f"Friend request sent to {friend_username}!"

# Function mostly made by ChatGPT: "Following the database structure, create a function that lets the user remove a friend"
def remove_friend(user_id, friend_username, client=None):
    """
    Removes the friend relationship between user_id and friend_username.
    First resolves friend_username to UserId, then deletes the friendship if it exists.
    """

    if client is None:
        client = bigquery.Client()

    # Resolve Username to UserId
    get_friend_id_query = """
    SELECT UserId FROM `keishlyanysanabriatechx25.bytemeproject.Users`
    WHERE Username = @friend_username
    """
    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("friend_username", "STRING", friend_username),
        ]
    )

    result = client.query(get_friend_id_query, job_config=job_config).result()
    rows = list(result)

    friend_id = rows[0]["UserId"]

    # Delete the friendship
    delete_query = """
    DELETE FROM `keishlyanysanabriatechx25.bytemeproject.Friends`
    WHERE (UserId1 = @user_id AND UserId2 = @friend_id)
       OR (UserId1 = @friend_id AND UserId2 = @user_id)
    """
    job_config_delete = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("user_id", "STRING", user_id),
            bigquery.ScalarQueryParameter("friend_id", "STRING", friend_id),
        ]
    )

    client.query(delete_query, job_config=job_config_delete).result()
    return f"Friendship with {friend_username} has been removed."

# Function created by ChatGPT: "create a function that checks the pending requests that the user_id currently has, it will be shown in an already created tab"
def get_pending_requests(user_id, client=None):
    """
    Returns a list of usernames who have sent a friend request to the given user_id.
    """

    if client is None:
        client = bigquery.Client()
    
    query = """
    SELECT U.Username AS SenderUsername, FR.RequesterId
    FROM `keishlyanysanabriatechx25.bytemeproject.FriendRequests` FR
    JOIN `keishlyanysanabriatechx25.bytemeproject.Users` U
    ON FR.RequesterId = U.UserId
    WHERE FR.ReceiverId = @user_id
    ORDER BY FR.RequestedAt DESC
    """

    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("user_id", "STRING", user_id)
        ]
    )

    results = client.query(query, job_config=job_config).result()

    return [{"username": row["SenderUsername"], "user_id": row["RequesterId"]} for row in results]

# Following 2 functions partially created by ChatGPT: "create the lines to accept and decline the friend requests. it should use the following functions to save/decline those friends: accept_friend_request"
def accept_friend_request(current_user_id, requester_id, client=None):
    if client is None:
        client = bigquery.Client()

    # Add friendship in one direction only
    insert_query = """
    INSERT INTO `keishlyanysanabriatechx25.bytemeproject.Friends` (UserId1, UserId2)
    VALUES (@user1, @user2)
    """

    insert_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("user1", "STRING", current_user_id),
            bigquery.ScalarQueryParameter("user2", "STRING", requester_id),
        ]
    )

    client.query(insert_query, job_config=insert_config).result()

    # Remove the friend request
    delete_query = """
    DELETE FROM `keishlyanysanabriatechx25.bytemeproject.FriendRequests`
    WHERE RequesterId = @requester_id AND ReceiverId = @receiver_id
    """

    delete_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("requester_id", "STRING", requester_id),
            bigquery.ScalarQueryParameter("receiver_id", "STRING", current_user_id),
        ]
    )

    client.query(delete_query, job_config=delete_config).result()

def decline_friend_request(current_user_id, requester_id, client=None):
    if client is None:
        client = bigquery.Client()

    query = """
    DELETE FROM `keishlyanysanabriatechx25.bytemeproject.FriendRequests`
    WHERE RequesterId = @requester_id AND ReceiverId = @receiver_id
    """

    config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("requester_id", "STRING", requester_id),
            bigquery.ScalarQueryParameter("receiver_id", "STRING", current_user_id),
        ]
    )

    client.query(query, job_config=config).result()

#the query was generated by gemini. i described the tables to it and then i asked it to create the query so that it returns the friend's workout data
def get_leaderboard_data(user_id, client=None):
    """
    Retrieves workout data for a given user and their friends
    (based on the Friends table with UserId1 and UserId2 columns)
    and structures it into a nested dictionary.

    Args:
        user_id (str): The UserId of the person you're interested in.

    Returns:
        dict: A dictionary where keys are UserIds (the initial user and their friends),
              and values are dictionaries containing 'distance', 'steps', and 'calories'.
    """
    if client is None:
        client = bigquery.Client(project="keishlyanysanabriatechx25")

    try:
        query = f"""
            SELECT
                u.Name,
                w.UserId,
                w.TotalDistance,
                w.TotalSteps,
                w.CaloriesBurned
            FROM
                `keishlyanysanabriatechx25.bytemeproject.Workouts` w
            JOIN
                `keishlyanysanabriatechx25.bytemeproject.Users` u ON w.UserId = u.UserId
            WHERE w.UserId = '{user_id}'
            UNION ALL
            SELECT
                u.Name,
                w.UserId,
                w.TotalDistance,
                w.TotalSteps,
                w.CaloriesBurned
            FROM
                `keishlyanysanabriatechx25.bytemeproject.Friends` f
            JOIN
                `keishlyanysanabriatechx25.bytemeproject.Workouts` w ON (f.UserId2 = w.UserId)
            JOIN
                `keishlyanysanabriatechx25.bytemeproject.Users` u ON w.UserId = u.UserId
            WHERE f.UserId1 = '{user_id}'
            UNION ALL
            SELECT
                u.Name,
                w.UserId,
                w.TotalDistance,
                w.TotalSteps,
                w.CaloriesBurned
            FROM
                `keishlyanysanabriatechx25.bytemeproject.Friends` f
            JOIN
                `keishlyanysanabriatechx25.bytemeproject.Workouts` w ON (f.UserId1 = w.UserId)
            JOIN
                `keishlyanysanabriatechx25.bytemeproject.Users` u ON w.UserId = u.UserId
            WHERE f.UserId2 = '{user_id}'
        """
        query_job = client.query(query)
        results = query_job.result()

        workout_data = {}
        for row in results:
            user_id = row.UserId
            name = row.Name
            distance = row.TotalDistance
            steps = row.TotalSteps
            calories = row.CaloriesBurned

            if user_id not in workout_data:
                workout_data[user_id] = {}

            workout_data[user_id] = {
                'name': name,
                'distance': distance,
                'steps': steps,
                'calories': calories
            }

        return workout_data

    except Exception as e:
        print(f"Error fetching BigQuery data: {e}")
        return None

def leaderboard_scoring_logic(user_id):
    # === PLACEHOLDER FOR ISSUE: Design, Implement and Test Leaderboard Scoring Logic (Darianne) ===
    pass

def save_goal(user_id):
    # === PLACEHOLDER FOR ISSUE: Design, Implement and Test Goal Creation Interface (Darianne) ===
    return "Achieve to burn 1000 calories in a week"
    #return goal?

def ai_call_for_planner(user_id):
    # === Design, Implement and Test AI Integration for Goal Planning (Daniela) ===
    # AI Response Format:
    # {
    #     "Day 1": [{"activity": "Running", "duration": "30 minutes", "calories_goal": 200}],
    #     ...
    # },
    # "general_tip": "Make sure to stretch before and after each workout."
    
    global _vertexai_initialized
    load_dotenv()
    if not _vertexai_initialized:
        import vertexai
        vertexai.init(project=os.environ.get("dagutierrez17techx25"), location="us-central1")
        _vertexai_initialized = True

    workouts = get_user_workouts(user_id) 
    goal = save_goal(user_id)
    model = GenerativeModel("gemini-1.5-flash-002")

    system_instruction = (
        "You are the lead fitness trainer for a fitness app. You're getting user past workouts "
        "in the 'workouts' list of dictionaries."
    )

    response = model.generate_content(f"""
        Based on the goal: '{goal}' and your knowledge of the user's past workouts: {workouts}, please generate a fitness plan. 
        Return a JSON dictionary with two keys: 
        1. "plan" → a dictionary where the keys are the days (e.g., 'Day 1', 'Day 2', ..., etc), and values are a list of recommended workouts for that day. 
           Each workout should be a dictionary with 'activity', 'duration', and 'calories_goal'.
        2. "general_tip" → a single helpful fitness tip relevant to the entire plan.

        Please provide specific exercises or types of activities. Take into consideration the user's past workouts to create a balanced and effective plan. The output should ONLY be a valid JSON dictionary, without any surrounding text or code blocks. Also please don't add line breaks.
    """)

    task_id = random.randint(1, 1000000)

    try:
        full_response = json.loads(response.text)

        plan_dictionary = full_response.get("plan", {})
        general_tip = full_response.get("general_tip", "")

        # Add "completed": False to each task in the plan
        for day in plan_dictionary:
            for task in plan_dictionary[day]:
                task["completed"] = False

        # Save the plan to GCS
        save_task_completion_to_gcs(user_id, task_id, plan_dictionary)

        return {
            'task_id': task_id,
            'content': plan_dictionary,
            'general_tip': general_tip
        }
    except json.JSONDecodeError as e:
        return {
            'task_id': task_id,
            'content': f"Error: Could not parse the AI response as a JSON dictionary. Raw response: {response.text}. Error details: {e}",
            'general_tip' : f"Error: Could not parse the AI response as a JSON dictionary. Raw response: {response.text}. Error details: {e}"
        }

def save_plan(user_id, ai_response, client=None):
    # === PLACEHOLDER FOR ISSUE: Design, Implement and Test Goal Plan Display UI (Kei) ===

    if client is None:
        client = bigquery.Client()

    # Extract values from the AI response
    task_id = ai_response.get("task_id")
    content_dict = ai_response.get("content", {})
    general_tip = ai_response.get("general_tip", "")

    # Safely convert content to JSON string (or leave error string if parsing failed)
    if isinstance(content_dict, dict):
        content_json = json.dumps(content_dict)
    else:
        content_json = str(content_dict)

    # Prepare the row to insert
    row = {
        "task_id": task_id,
        "user_id": user_id,
        "content": content_json,
        "general_tip": general_tip
    }

    # Define table ID
    table_id = "keishlyanysanabriatechx25.bytemeproject.UserTaskPlans"

    # Insert the row
    errors = client.insert_rows_json(table_id, [row])

    if errors:
        print(f"❌ Failed to insert into BigQuery: {errors}")
    else:
        print("✅ Plan successfully saved to BigQuery!")

# Function to save task completion data as a JSON blob in GCS
def save_task_completion_to_gcs(user_id, task_id, plan_dict):
    from google.cloud import storage

    bucket_name = 'byte-me-user-tasks'
    blob_name = f'task_completion/completed_{user_id}_{task_id}.json'

    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(blob_name)

    json_data = json.dumps(plan_dict)
    blob.upload_from_string(json_data, content_type='application/json')

# Function to read task completion data from GCS
def read_task_completion_from_gcs(user_id, task_id):
    from google.cloud import storage

    bucket_name = 'byte-me-user-tasks'
    blob_name = f'task_completion/completed_{user_id}_{task_id}.json'

    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(blob_name)

    if blob.exists():
        data = blob.download_as_string()
        return json.loads(data)
    else:
        return None  # Or raise an exception if needed

# Function to mark task completion and update the GCS blob
def mark_task(user_id, task_id, day_label, task_index, new_state):
    task_data = read_task_completion_from_gcs(user_id, task_id)
    if not task_data:
        print("Task data not found.")
        return

    try:
        task_data[day_label][task_index]["completed"] = new_state
        save_task_completion_to_gcs(user_id, task_id, task_data)
        print(f"Task updated successfully.")
    except Exception as e:
        print(f"Error updating task: {e}")

def get_progress_data(user_id, task_id, client=None):
    # === PLACEHOLDER FOR ISSUE: Design, Implement and Test Goal Progress Tracking (Ariana) ===

    if client is None:
        client = bigquery.Client()

    query = f"""
        SELECT content
        FROM `bytemeproject.UserTaskPlans`
        WHERE user_id = @user_id AND task_id = @task_id
        LIMIT 1
    """
    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("user_id", "STRING", user_id),
            bigquery.ScalarQueryParameter("task_id", "STRING", task_id),
        ]
    )
    query_job = client.query(query, job_config=job_config)
    results = list(query_job.result())

    if not results:
        return {}

    # Deserialize JSON plan
    content = results[0].content
    try:
        plan = json.loads(content)
        return plan
    except json.JSONDecodeError:
        return {}
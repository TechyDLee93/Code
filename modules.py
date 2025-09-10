#############################################################################
# modules.py
#
# This file contains modules that may be used throughout the app.
#
# You will write these in Unit 2. Do not change the names or inputs of any
# function other than the example.
#############################################################################

import streamlit as st
from internals import create_component
import pandas as pd
import matplotlib.pyplot as plt

# Import for display_post
import requests
import base64
from data_fetcher import get_user_posts, get_genai_advice, get_user_profile, get_user_sensor_data, get_user_workouts, get_friend_data, send_friend_request, remove_friend, get_leaderboard_data, leaderboard_scoring_logic, save_goal, ai_call_for_planner, mark_task, get_progress_data, get_pending_requests, accept_friend_request, decline_friend_request


# Import for user_profile
import datetime
from google.cloud import bigquery

# This one has been written for you as an example. You may change it as wanted.
def display_my_custom_component(value):
    """Displays a 'my custom component' which showcases an example of how custom
    components work.

    value: the name you'd like to be called by within the app
    """
    # Define any templated data from your HTML file. The contents of
    # 'value' will be inserted to the templated HTML file wherever '{{NAME}}'
    # occurs. You can add as many variables as you want.
    data = {
        'NAME': value,
    }
    # Register and display the component by providing the data and name
    # of the HTML file. HTML must be placed inside the "custom_components" folder.
    html_file_name = "my_custom_component"
    create_component(data, html_file_name)

# Function partially created by Copilot and Claude with "implement display_post to look like the image: (insert Mockup of display_post)"
def display_post(username, user_image, timestamp, content, post_image=None):
    """Displays a post with the given details.

    Args:
        username (str): The username of the person who made the post.
        user_image (str): The URL or path to the user's profile image.
        timestamp (str): The time when the post was made.
        content (str): The content of the post.
        post_image (str, optional): The URL or path to the image associated with the post.
                                   If None or invalid, no image will be displayed.
    """
    post = {
        "timestamp": timestamp,
        "post_image": post_image,
        "username": username,
        "content": content,
        "user_image": user_image
    }

    def is_valid_image(url):
        """Checks if a given URL is a valid image."""
        try:
            print(f"Attempting to fetch: {url}") #added print statement
            response = requests.get(url, stream=True, timeout=5)
            print(f"Response status: {response.status_code}") #added print statement
            content_type = response.headers.get('Content-Type', '')
            print(f"Content type: {content_type}") #added print statement
            return response.status_code == 200 and 'image' in content_type
        except requests.RequestException as e:
            print(f"Request exception: {e}") #added print statement
            return False

    # Check if post_image is provided and valid
    if post['post_image'] and not is_valid_image(post['post_image']):
        # If invalid, just set to None and inform the user
        st.warning("Invalid image URL. Your post will be created without an image.")
        post['post_image'] = None

    # Custom CSS and HTML rendering
    st.markdown(
        """
        <style>
        .post-container {
            border-radius: 10px;
            overflow: hidden;
            border: 1px solid #ddd;
        }
        .user-box {
            background-color: #4285F4;
            padding: 10px;
        }
        .user-row {
            display: flex;
            align-items: center;
        }
        .user-row img {
            border-radius: 50%;
            margin-right: 10px;
            height: 50px;
            width: 50px;
            object-fit: cover;
        }
        .timestamp-row {
            background-color: #FBBC05;
            padding: 10px;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 50px;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    # Handle None values
    username_display = post['username'] if post['username'] else ""
    user_image_display = post['user_image'] if post['user_image'] else ""
    content_display = post['content'] if post['content'] else ""
    timestamp_display = post['timestamp'] if post['timestamp'] else ""

    # Create HTML content based on whether post_image is available or not
    if post['post_image']:
        html_content = f"""
        <div class="post-container">
            <div class="user-box">
                <div class="user-row">
                    <img src="{user_image_display}">
                    <h3>{username_display}</h3>
                </div>
                <p>{content_display}</p>
            </div>
            <img src="{post['post_image']}" style="width: 100%; height: auto;">
            <div class="timestamp-row">
                <p>Posted on: {timestamp_display}</p>
            </div>
        </div>
        """
    else:
        # No image version - skip the image tag entirely
        html_content = f"""
        <div class="post-container">
            <div class="user-box">
                <div class="user-row">
                    <img src="{user_image_display}">
                    <h3>{username_display}</h3>
                </div>
                <p>{content_display}</p>
            </div>
            <div class="timestamp-row">
                <p>Posted on: {timestamp_display}</p>
            </div>
        </div>
        """
    
    st.markdown(html_content, unsafe_allow_html=True)

def display_activity_summary(workouts_list):
    # Convert the workouts data into a DataFrame for easy display
    df = pd.DataFrame(workouts_list)

    # Display a table with the workout summary
    st.subheader("Activity Summary")
    st.dataframe(df)

    # Create a bar plot of the distance vs. calories burned
    #GEN AI citation: I asked AI for help to determine the correct values for the graph, ensuring values are displayed accurately
    fig, ax = plt.subplots()
    ax.bar(df['StartTimestamp'], df['distance'], color='blue', label='Distance (km)')
    ax.set_xlabel('Start Time')
    ax.set_ylabel('Distance (km)')
    ax.set_title('Distance vs. Time')

    # Add another bar plot for calories burned
    ax2 = ax.twinx()
    ax2.plot(df['StartTimestamp'], df['calories_burned'], color='red', label='Calories', marker='o')
    ax2.set_ylabel('Calories')
    ax2.legend(loc='upper left')

    st.pyplot(fig)


def display_recent_workouts(workouts_list):
    if not workouts_list:
        st.write("No recent workouts. Let's get started!")
        return

    #Gemini was used in this method to create the table using DataFrame
    # Sort workouts by start time (most recent first)
    workouts_list.sort(key=lambda x: x['StartTimestamp'], reverse=True)

    # Convert workouts_list into a DataFrame for easier display in table form
    df = pd.DataFrame(workouts_list)

    # Rename columns for better readability
    df.columns = ['Workout ID', 'Start Time', 'End Time', 'Start Location', 'End Location', 'Distance (km)', 'Steps', 'Calories Burned']

    st.write("Here is a list of your most recent workout(s):")
    
    # Display the DataFrame as a table
    st.table(df)


def display_genai_advice(timestamp, content, image):

    genai_advice = get_genai_advice('user1') #get data from data_fetcher

    #get timestamp and display it 
    timestamp = genai_advice['timestamp']
    if timestamp is not None:
        st.subheader(f" :blue[{timestamp}]", divider="green")
    else:
        st.subheader(f" :blue[No timestamp available]", divider="green")

    #get motivational message and display it
    content = genai_advice['content']
    if content is not None:
        st.title(f" :red[{content}]")
    else:
        st.title(f" :red[No motivational message available]")

    #get image and display it  
    image = genai_advice['image']
    if image is not None:
        st.image(image)
    else:
        st.title(f" :red[No image available]")

def display_sensor_data(sensor_list):

    st.title("User Sensor Data Viewer")

    #if user_id and workout_id:
    #sensor_data_df = get_user_sensor_data(user_id, workout_id)

    if sensor_list is not None:
        #st.subheader(f"Sensor Data for User: {user_id}, Workout: {workout_id}")
        st.dataframe(sensor_list)  # Display as a nice interactive table
    #elif sensor_list is not None and sensor_list.empty:
        #st.info("No sensor data found for the specified User ID and Workout ID.")
    else:
        st.warning("Invalid User ID and Workout ID.")

def display_user_profile(user_id):
    """Displays the user profile information in a well-formatted layout.
    
    Args:
        user_id (str): The ID of the user whose profile is being displayed.
    """
    # Get user profile data
    user_profile = get_user_profile(user_id)
    
    if not user_profile:
        st.error(f"User profile not found for ID: {user_id}")
        return
    
    # Create layout with columns
    col1, col2 = st.columns([1, 2])
    
    # Profile image and basic info
    with col1:
        if user_profile.get("profile_image"):
            st.image(user_profile["profile_image"], width=200)
        else:
            # Display placeholder if no image
            st.image("https://via.placeholder.com/200x200?text=No+Image", width=200)
        
        st.write(f"**@{user_profile['username']}**")
        
        # Add buttons for actions
        #st.button("Edit Profile")
        #st.button("Add Friend")
        st.button("Edit Profile", key=f"edit_profile_{user_id}")
        st.button("Add Friend", key=f"add_friend_{user_id}")

    
    # User details in right column
    with col2:
        st.header(user_profile["full_name"])
        
        # Format and display date of birth
        if user_profile.get("date_of_birth"):
            dob = user_profile["date_of_birth"]
            if isinstance(dob, str):
                st.write(f"**Date of Birth:** {dob}")
            else:
                st.write(f"**Date of Birth:** {dob.strftime('%B %d, %Y')}")
        
        # Friends count
        friend_count = len(user_profile.get("friends", []))
        st.write(f"**Friends:** {friend_count}")
        
        # Additional profile stats could go here
        # Example: posts count
        posts = get_user_posts(user_id)
        st.write(f"**Posts:** {len(posts)}")
    
    # Display tabs for different sections of the profile
    profile_tabs = st.tabs(["Posts", "Friends", "Activity"])
    
    # Posts tab
    with profile_tabs[0]:
        posts = get_user_posts(user_id)
        if posts:
            for post in posts:
                with st.container():
                    st.markdown(f"**{post['timestamp']}**")
                    st.write(post['content'])
                    
                    if post.get('image'):
                        st.image(post['image'])
                    
                    st.divider()
        else:
            st.write("No posts yet.")
    
    # Friends tab
    with profile_tabs[1]:
        if user_profile.get("friends") and len(user_profile["friends"]) > 0:
            # Create grid layout for friends
            friends_per_row = 4
            num_friends = len(user_profile["friends"])
            
            for i in range(0, num_friends, friends_per_row):
                cols = st.columns(min(friends_per_row, num_friends - i))
                
                for j in range(min(friends_per_row, num_friends - i)):
                    with cols[j]:
                        friend_id = user_profile["friends"][i + j]
                        friend_profile = get_user_profile(friend_id)
                        
                        if friend_profile:
                            if friend_profile.get("profile_image"):
                                st.image(friend_profile["profile_image"], width=100)
                            else:
                                st.image("https://via.placeholder.com/100x100?text=No+Image", width=100)
                            
                            st.write(f"**{friend_profile['username']}**")
                            st.write(friend_profile["full_name"])
                        else:
                            st.write(f"Friend ID: {friend_id}")
                            st.write("(Profile unavailable)")
        else:
            st.write("No friends added yet.")
    
    # Activity tab
    with profile_tabs[2]:
        # Assuming you have a function to get user workouts
        try:
            workouts = get_user_workouts(user_id)
            if workouts and len(workouts) > 0:
                # Sort workouts by start time (most recent first)
                workouts.sort(key=lambda x: x['StartTimestamp'], reverse=True)
                
                # Take only 5 most recent
                recent_workouts = workouts[:5]
                
                for workout in recent_workouts:
                    with st.container():
                        # Format timestamp
                        start_time = workout['StartTimestamp']
                        formatted_time = start_time
                        if isinstance(start_time, datetime.datetime):
                            formatted_time = start_time.strftime('%Y-%m-%d %H:%M')
                        
                        st.write(f"**Workout on {formatted_time}**")
                        
                        # Create columns for workout stats
                        stat_cols = st.columns(3)
                        
                        with stat_cols[0]:
                            st.metric("Distance", f"{workout.get('Distance (km)', 0):.2f} km")
                        
                        with stat_cols[1]:
                            st.metric("Steps", workout.get('Steps', 0))
                        
                        with stat_cols[2]:
                            st.metric("Calories", workout.get('Calories Burned', 0))
                        
                        st.divider()
            else:
                st.write("No workout activity recorded yet.")
        except Exception as e:
            st.write("Unable to load activity data.")
            st.error(str(e))

def friend_request_ui(user_id):
    # === PLACEHOLDER FOR ISSUE: Design, Implement and Test Friend Request Functionality (Kei) ===
    """
    Note: This function will call get_friend_data in data_fetcher.py to get the data of 
    the friend and send/receive friend requests for it to be reflected in the database
    """
    st.header("Friend Network")
    
    # Create tabs for different friend-related functions
    tab1, tab2 = st.tabs(["Search Users", "Pending Requests"])
    
    # Tab 1: Search for users to send friend requests
    with tab1:
        st.subheader("Find Friends")
        friend_username = st.text_input("Search for users by username")
        
        if friend_username:
            search_results = get_friend_data(user_id, friend_username)

            st.write(search_results)

            if search_results == f"You and '{friend_username}' are not friends yet.":
                if st.button(f"Send Friend Request to {friend_username}"):
                    send_friend_request(user_id, friend_username)
                    st.success(f"Friend request sent to {friend_username}!")
            elif search_results == f"You and '{friend_username}' are friends.":
                if st.button(f"Remove Friend"):
                    remove_friend(user_id, friend_username)
                    st.success(f"Removed {friend_username} from your friends.")
    
    # Tab 2: Users can see their pending requests
    with tab2:
        st.subheader("Requests You've Received")
        pending_requests = get_pending_requests(user_id)

        if not pending_requests:
            st.info("No pending friend requests.")
        else:
            for req in pending_requests:
                with st.container():
                    st.write(f"👤 {req['username']} sent you a friend request.")
                    col1, col2 = st.columns([1, 1])

                    with col1:
                        if st.button(f"✅ Accept {req['username']}", key=f"accept_{req['user_id']}"):
                            accept_friend_request(user_id, req['user_id'])
                            st.success(f"You are now friends with {req['username']}!")
                            st.rerun()

                    with col2:
                        if st.button(f"❌ Decline {req['username']}", key=f"decline_{req['user_id']}"):
                            decline_friend_request(user_id, req['user_id'])
                            st.info(f"Declined friend request from {req['username']}.")
                            st.rerun()

#created with help from gemini, asked it to create a leaderboard table based on leaderboard_data and to then also add the
#friend's profile functionality
def create_leaderboard_ui(user_id):
    st.title("Friends Leaderboard")
    st.write("Select the metric you want to see the leaderboard based on:")

    leaderboard_data = get_leaderboard_data(user_id)

    if not leaderboard_data:
        st.warning("No workout data found for you or your friends.")
        return

    df_leaderboard = pd.DataFrame.from_dict(leaderboard_data, orient='index')
    df_leaderboard.index.name = 'UserId'
    df_leaderboard = df_leaderboard.reset_index()

    def get_full_name(uid):
        profile = get_user_profile(uid)
        return profile.get('full_name', 'Unknown')

    df_leaderboard['Name'] = df_leaderboard['UserId'].apply(get_full_name)

    sort_option = st.radio("Sort by:", ('Calories Burned', 'Total Steps', 'Total Distance'))

    if sort_option == 'Calories Burned':
        sort_by = 'calories'
        display_name = 'Calories Burned'
        columns_to_display = ['Name', 'calories']
        column_renaming = {'calories': 'Calories Burned'}
    elif sort_option == 'Total Steps':
        sort_by = 'steps'
        display_name = 'Total Steps'
        columns_to_display = ['Name', 'steps']
        column_renaming = {'steps': 'Total Steps'}
    elif sort_option == 'Total Distance':
        sort_by = 'distance'
        display_name = 'Total Distance'
        columns_to_display = ['Name', 'distance']
        column_renaming = {'distance': 'Total Distance'}
    else:
        return

    sorted_leaderboard = df_leaderboard.sort_values(by=sort_by, ascending=False).reset_index(drop=True)
    sorted_leaderboard.index = sorted_leaderboard.index + 1

    st.subheader(f"Leaderboard by {display_name}")
    st.table(sorted_leaderboard[columns_to_display].rename(columns=column_renaming))

    # Profile viewing logic - no automatic calls
    selected_user_id = st.selectbox(
        "Select a friend to view their profile:",
        sorted_leaderboard['UserId'],
        format_func=get_full_name
    )

    #Prevent profile from rendering automatically:
    if st.button(f"View Profile of {get_full_name(selected_user_id)}", key=f"view_profile_{selected_user_id}"):
        # Use st.session_state to remember the selection
        st.session_state['selected_profile_to_display'] = selected_user_id

    #Only display the profile if the user has explicitly clicked the button
    if 'selected_profile_to_display' in st.session_state:
        st.markdown("---")
        display_user_profile(st.session_state['selected_profile_to_display'])

def goal_creation_ui(user_id):
    # === PLACEHOLDER FOR ISSUE: Design, Implement and Test Goal Creation Interface (Darianne) ===
    """
    Note: This function will call save_goal in data_fetcher.py to save the data of 
    the goal that the user submitted.

    Hint: You can check if the goal is unrealistic by implementing an AI that you can check with
    every time that the user submits a goal.
    """
    pass

def goal_plan_display_ui(user_id):
    # === PLACEHOLDER FOR ISSUE: Design, Implement and Test Goal Plan Display UI (Kei) ===
    """
    Note: This function will call ai_call_for_planner in data_fetcher.py to show the data that
    is returned in said function. It also calls mark_task to mark/unmark a task as completed and for
    it to be reflected in the database.
    """
    #goal = save_goal(user_id)
    ai_response = ai_call_for_planner(user_id)

    if 'content' in ai_response and isinstance(ai_response['content'], dict):
        plan = ai_response['content']
        task_id = ai_response['task_id']
        st.markdown(f"<h2 style='font-size: 1.5em;'>Your Fitness Plan</h2>", unsafe_allow_html=True)

        # Google colors
        google_blue = "#4285F4"
        google_red = "#DB4437"
        google_yellow = "#F4B400"
        google_green = "#0F9D58"
        colors = [google_blue, google_red, google_yellow, google_green]
        color_index = 0

        completed_tasks = st.session_state.get(f"completed_tasks_{task_id}", {})
        table_data = []

        for day, activities in plan.items():
            tasks_html_list = []
            if isinstance(activities, list):
                for i, activity in enumerate(activities):
                    key = f"{task_id}_{day}_{i}"
                    completed = completed_tasks.get(key, False)
                    checkbox_id = f"checkbox_{key}"
                    checked_attribute = "checked" if completed else ""
                    checkbox_html = f'<input type="checkbox" id="{checkbox_id}" {checked_attribute} onchange="handleCheckboxChange(\'{key}\')">'
                    label_html = f'<label for="{checkbox_id}">{activity}</label>'
                    task_html = f"{checkbox_html} <span style='margin-left: 0.5em;'>{label_html}</span>" # Add spacing
                    tasks_html_list.append(task_html)
            else:
                key = f"{task_id}_{day}"
                completed = completed_tasks.get(key, False)
                checkbox_id = f"checkbox_{key}"
                checked_attribute = "checked" if completed else ""
                checkbox_html = f'<input type="checkbox" id="{checkbox_id}" {checked_attribute} onchange="handleCheckboxChange(\'{key}\')">'
                label_html = f'<label for="{checkbox_id}">{activities}</label>'
                task_html = f"{checkbox_html} <span style='margin-left: 0.5em;'>{label_html}</span>" # Add spacing
                tasks_html_list.append(task_html)

            table_data.append({'Day': f"<span style='color: {colors[color_index % len(colors)]}; font-weight: bold;'>{day}</span>",
                               'Tasks': "<br>".join(tasks_html_list)})
            color_index += 1

        if table_data:
            df = pd.DataFrame(table_data)
            st.markdown(df.to_html(index=False, escape=False), unsafe_allow_html=True)
            st.markdown("""
            <script>
            function handleCheckboxChange(key) {
            const isChecked = document.getElementById('checkbox_' + key).checked;
            fetch('/_stcore/update_state', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ key: 'checkbox_' + key, value: isChecked })
            }).then(() => {
                // State is managed by Streamlit
            });
            }
            </script>
            """, unsafe_allow_html=True)

            # Call mark_task_completed based on session state
            if f"completed_tasks_{task_id}" in st.session_state:
                for key, completed in st.session_state[f"completed_tasks_{task_id}"].items():
                    day_from_key = key.split('_')[0] if '_' in key else "" # Extract day if possible
                    #mark_task_completed(user_id, task_id, day_from_key, completed)

        st.markdown("""
        <hr style="border:1px solid #ccc;">
        <p style="font-size: 0.8em; color: gray;">
            <b>Disclaimer:</b> Please be aware that this fitness plan was generated by an AI and may not be perfectly tailored to your individual needs and health conditions. It is essential to consult with a doctor or qualified healthcare professional before starting any new fitness regimen to ensure it is safe and appropriate for you.
        </p>
        """, unsafe_allow_html=True)

    else:
        st.error("Failed to retrieve or process the fitness plan.")
        if 'content' in ai_response:
            st.write(f"Raw AI Response: {ai_response['content']}")

def goal_progress_tracking_ui(user_id, task_id):
    # === PLACEHOLDER FOR ISSUE: Design, Implement and Test Goal Progress Tracking (Ariana) ===
    """
    Note: Calls get_progress_data in data_fetcher.py to make sure the 
    user's progress data of the specific task_id is properly stored and retrieved from database.
    """
    pass

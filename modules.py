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
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Import for display_post
import requests
import base64
from data_fetcher import get_user_posts, get_genai_advice, get_user_profile, get_user_sensor_data, get_user_workouts

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

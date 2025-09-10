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

# Function partially created by Copilot with "implement display_post to look like the image: (insert Mockup of display_post)"
def display_post(username, user_image, timestamp, content, post_image):
    """Displays a post with the given details.

    Args:
        username (str): The username of the person who made the post.
        user_image (str): The URL or path to the user's profile image.
        timestamp (str): The time when the post was made.
        content (str): The content of the post.
        post_image (str): The URL or path to the image associated with the post.
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

    # Check if the post_image URL is valid
    if post['post_image'] and not is_valid_image(post['post_image']):
        st.warning("Invalid image URL. Please upload a valid image.")

        # Handle the file upload
        uploaded_file = st.file_uploader("Upload an image:", type=["jpg", "jpeg", "png", "gif"])

        if uploaded_file:
            # Read the uploaded file as a binary stream and convert to base64
            encoded_image = base64.b64encode(uploaded_file.getvalue()).decode("utf-8")
            # Save the image to session state
            st.session_state.post_image = f"data:image/jpeg;base64,{encoded_image}"
            post['post_image'] = st.session_state.post_image

        else:
            # Use placeholder if no valid image is provided
            st.session_state.post_image = "https://via.placeholder.com/600x400?text=No+Image"
            post['post_image'] = st.session_state.post_image
    elif not post['post_image']:
        st.session_state.post_image = "https://via.placeholder.com/600x400?text=No+Image"
        post['post_image'] = st.session_state.post_image

    # Custom CSS and HTML rendering
    st.markdown(
        """
        <style>
        .post-container {
            border-radius: 10px; /* Rounded corners here! */
            overflow: hidden; /* Ensure child elements respect the border radius */
            border: 1px solid #ddd; /* Optional: Add a border for better visibility */
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

    st.markdown(
        f"""
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
        """,
        unsafe_allow_html=True
    )


def display_activity_summary(workouts_list):
    """Write a good docstring here."""
    pass


def display_recent_workouts(workouts_list):
    pass


def display_genai_advice(timestamp, content, image):

    genai_advice = get_genai_advice('user1') #get data from data_fetcher

    #get timestamp and display it 
    timestamp = genai_advice['timestamp']
    st.subheader(f" :blue[{timestamp}]", divider="green")

    #get motivational message and display it
    content = genai_advice['content']
    st.title(f" :red[{content}]")

    #get image and display it 
    image = genai_advice['image']
    st.image(image)

#############################################################################
# app.py
#
# This file contains the entrypoint for the app.
#
#############################################################################

import streamlit as st
from modules import display_my_custom_component, display_post, display_genai_advice, display_activity_summary, display_recent_workouts
from data_fetcher import get_user_posts, get_genai_advice, get_user_profile, get_user_sensor_data, get_user_workouts

# New imports
from datetime import datetime

userId = 'user1'

# Created tabs and display post code by Copilot using the following prompt: "create a streamlit app that showcases a post. that post will have a timestamp, post_image, username, content (of the post), and user_image."
def display_app_page():
    """Displays the home page of the app."""
    st.title('Welcome to SDS!')

    # Create tabs
    tab1, tab2 = st.tabs(["Home", "Posts"])

    with tab1:
        # An example of displaying a custom component called "my_custom_component"
        value = st.text_input('Enter your name')
        display_my_custom_component(value)
        
    with tab2:
        # Sample data
        post = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "post_image": "https://upload.wikimedia.org/wikipedia/commons/c/c8/Puma_shoes.jpg",
            "username": "John Doe",
            "content": "This is a sample post content. Streamlit makes it easy to create beautiful apps.",
            "user_image": "https://upload.wikimedia.org/wikipedia/commons/c/c8/Puma_shoes.jpg"
        }

        display_post(post["username"], post["user_image"], post["timestamp"], post["content"], post["post_image"])


    #call get genAI advice
    advice = get_genai_advice(userId)
    #call method in modules that displays the genAI advice
    display_genai_advice(advice['timestamp'], advice['content'], advice['image'])


# This is the starting point for your app. You do not need to change these lines
if __name__ == '__main__':
    display_app_page()

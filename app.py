#############################################################################
# app.py
#
# This file contains the entrypoint for the app.
#
#############################################################################

import streamlit as st
from modules import display_my_custom_component, display_post, display_genai_advice, display_activity_summary, display_recent_workouts, display_sensor_data
from data_fetcher import get_user_posts, get_genai_advice, get_user_profile, get_user_sensor_data, get_user_workouts

# New imports
from datetime import datetime
from google.cloud import bigquery

# Created tabs and display post code by Copilot using the following prompt: "create a streamlit app that showcases a post. that post will have a timestamp, post_image, username, content (of the post), and user_image."
def display_app_page():
    """Displays the home page of the app."""
    st.title('Welcome to SDS!')

    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["Home", "GenAI Advice", "Activity Summary", "Recent Workouts", "Sensor Data", "Community"])
    userId = None # Example data

    with tab1:
        # An example of displaying a custom component called "my_custom_component"
        value = st.text_input('Enter your name')
        display_my_custom_component(value)

        # Get data
        userId = 'user3'
        posts = get_user_posts(userId)  # Fetch a list of posts
        for post in posts: # Show every post
            display_post(post["username"], post["user_image"], post["timestamp"], post["content"], post["image"])
        
    with tab2:
        advice = get_genai_advice(userId)
        #call method in modules that displays the genAI advice
        display_genai_advice(advice['timestamp'], advice['content'], advice['image'])
    
    with tab3:
        # Fetch user workouts and display activity summary
        userId = 'user1'
        workouts = get_user_workouts(userId)  # Fetch workouts for the user
        display_activity_summary(workouts)  # Pass workouts to display activity summary

    with tab4:
        userId = 'user1'
        workouts = get_user_workouts(userId)
        display_recent_workouts(workouts)

    with tab5:
        userId = 'user1'
        sensor_data = get_user_sensor_data(userId, 'workout1')
        display_sensor_data(sensor_data)

    with tab6:
        client = bigquery.Client()
        

        def display_all_posts():

            posts = get_user_posts(userId)
            if posts:
                for post in posts:
                    user_id = post.get('user_id', 'Unknown')
                    timestamp = post.get('timestamp', 'No timestamp')
                    content = post.get('content', 'No content')
                    image_url = post.get('image', '')

                    st.write(f"\nWhat's on your mind: {user_id} - {timestamp}: {content}")

                    if image_url and isinstance(image_url, str) and image_url.startswith("http"):
                        try:
                            st.image(image_url, width=150)
                        except Exception as e:
                            st.error(f"Error displaying image from URL: {e}")
                    else:
                        st.write("Image not available.")
            else:
                st.write("No posts available.")

 
        def display_community_page(user_id):
             
             genai_advice = get_genai_advice(user_id)
             user_profile = get_user_profile(user_id)
 
             if user_profile:
                 st.write(f"User Profile: {user_profile['full_name']} (@{user_profile['username']})")
                 st.image(user_profile['profile_image'], width=100)
                 st.write("News Feed:")
                 display_all_posts()
                 st.write("\nAdvice & Encouragement:")
                 if genai_advice:
                     st.write(f"Advice: {genai_advice['content']}")
                     if genai_advice['image']:
                        st.image(genai_advice['image'], width=150)
                 else:
                     st.write("No GenAI advice found.")
             else:
                 st.write(f'user {user_id} not found')
        display_community_page(userId)

# This is the starting point for your app. You do not need to change these lines
if __name__ == '__main__':
    display_app_page()

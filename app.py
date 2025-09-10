#############################################################################
# app.py
#
# This file contains the entrypoint for the app.
#
#############################################################################

import streamlit as st
from modules import display_my_custom_component, display_post, display_genai_advice, display_activity_summary, display_recent_workouts, display_sensor_data, display_user_profile, friend_request_ui, create_leaderboard_ui, goal_creation_ui, goal_plan_display_ui, goal_progress_tracking_ui
from data_fetcher import get_user_posts, get_genai_advice, get_user_profile, get_user_sensor_data, get_user_workouts, add_post_to_database, get_friend_data, send_friend_request, remove_friend, get_leaderboard_data, leaderboard_scoring_logic, save_goal, ai_call_for_planner, mark_task, get_progress_data

# New imports
from datetime import datetime
from google.cloud import bigquery

# Created tabs and display post code by Copilot using the following prompt: "create a streamlit app that showcases a post. that post will have a timestamp, post_image, username, content (of the post), and user_image."
def display_app_page():
    """Displays the home page of the app."""
    st.title('Welcome to SDS!')

    tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9, tab10 = st.tabs(["Home", "GenAI Advice", "Activity Summary", "Recent Workouts", "Sensor Data", "Community", "Activity Page", "User Profile", "Friends-Only Leaderboard", "Planner"])
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
    
    # Partially created by Claude AI: "Create a tab that displays activity page with given instructions"
    with tab7:
        # New User Activity tab that integrates all required components
        userId = 'user1'
        workouts = get_user_workouts(userId)
       
        # Display user activity page
        st.header("Your Activity Dashboard")
       
        # Display recent 3 workouts
        if workouts:
            # Sort workouts by start time (most recent first)
            workouts.sort(key=lambda x: x['StartTimestamp'], reverse=True)
            # Get only the 3 most recent workouts
            recent_workouts = workouts[:3]
            display_recent_workouts(recent_workouts)
        else:
            st.write("No recent workouts. Let's get started!")
       
        # Display activity summary
        if workouts:
            display_activity_summary(workouts)
        else:
            st.write("No activity data available yet.")
       
        # Share section
        st.header("Share Your Achievement")
       
        # Calculate stats to share (if workouts exist)
        if workouts:
            total_steps = sum(workout.get('steps', 0) for workout in workouts)
            total_distance = sum(workout.get('distance', 0) for workout in workouts)
            total_calories = sum(workout.get('calories_burned', 0) for workout in workouts)
           
            # Create columns for share buttons
            col1, col2, col3 = st.columns(3)
           
            with col1:
                if st.button(f"Share Steps: {total_steps}"):
                    post_content = f"I've taken {total_steps} steps in my fitness journey! #FitnessGoals"
                    add_post_to_database(userId, post_content)
                    st.success("Post shared successfully!")
           
            with col2:
                if st.button(f"Share Distance: {total_distance:.2f} km"):
                    post_content = f"I've covered {total_distance:.2f} km so far! #ActiveLifestyle"
                    add_post_to_database(userId, post_content)
                    st.success("Post shared successfully!")
           
            with col3:
                if st.button(f"Share Calories: {total_calories} burned"):
                    post_content = f"I've burned {total_calories} calories through my workouts! #HealthyLiving"
                    add_post_to_database(userId, post_content)
                    st.success("Post shared successfully!")
                   
            # Option to share latest workout
            latest_workout = workouts[0]  # First workout is the most recent after sorting
            if st.button("Share Latest Workout"):
                latest_steps = latest_workout.get('Steps', 0)
                latest_distance = latest_workout.get('Distance (km)', 0)
                latest_calories = latest_workout.get('Calories Burned', 0)
                post_content = f"Just completed a workout! {latest_steps} steps, {latest_distance:.2f} km, and burned {latest_calories} calories! #WorkoutComplete"
                add_post_to_database(userId, post_content)
                st.success("Latest workout shared!")
        else:
            st.write("Complete workouts to unlock sharing!")
    
    with tab8:
        # Display user profile
        userId = 'user1'  # You can use the current logged-in user's ID here
        display_user_profile(userId)  # Call the profile display function
    
    # Tab of Friends-Only Leaderboard
    with tab9:
        userId = 'user1'  # You can use the current logged-in user's ID here
        # === PLACEHOLDER FOR ISSUE: Design, Implement and Test Friends-Only Leaderboard UI (Ariana) ===
            # Call create_leaderboard_ui from modules.py 
        user_id = 'user1'
        create_leaderboard_ui(user_id)
        # === PLACEHOLDER FOR ISSUE: Design, Implement and Test Friend Request Functionality (Kei) ===
            # Call friend_request_ui from modules.py
        friend_request_ui(userId)
    
    # Tab of AI Planner
    with tab10:
        # === PLACEHOLDER FOR ISSUE: Design, Implement and Test Goal Creation Interface (Darianne) ===
            # Call goal_creation_ui from modules.py
        # === PLACEHOLDER FOR ISSUE: Design, Implement and Test Goal Plan Display UI (Kei) ===
            # Call goal_plan_display_ui from modules.py 
        user_id = 'user1'
        goal_plan_display_ui(user_id)
        # === PLACEHOLDER FOR ISSUE: Design, Implement and Test Goal Progress Tracking (Ariana) ===
            # Call goal_progress_tracking_ui from modules.py 
        pass

        

# This is the starting point for your app. You do not need to change these lines
if __name__ == '__main__':
    display_app_page()

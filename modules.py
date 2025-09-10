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


def display_post(username, user_image, timestamp, content, post_image):
    """Write a good docstring here."""
    pass


def display_activity_summary(workouts_list):
    """Write a good docstring here."""
    pass


def display_recent_workouts(workouts_list):
    pass


def display_genai_advice(timestamp, content, image):
<<<<<<< HEAD
=======
    
>>>>>>> 1833dc1 (update modules with genai advice implementation)
    genai_advice = get_genai_advice('user1')

    timestamp = genai_advice['timestamp']
    st.subheader(f" :blue[{timestamp}]", divider="green")

    content = genai_advice['content']
    st.title(f" :red[{content}]")

    image = genai_advice['image']
    st.image(image)
<<<<<<< HEAD
=======




    
>>>>>>> 1833dc1 (update modules with genai advice implementation)

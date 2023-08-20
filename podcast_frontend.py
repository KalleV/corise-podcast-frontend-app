import streamlit as st
import modal
import json
import os
import validators

def validate_url(url):
    """
    Function that validates a given URL.

    Args:
        url (str): The URL to validate.

    Returns:
        bool: True if the URL is valid, False otherwise.
    """
    if not validators.url(url):
        st.sidebar.error("Invalid URL")
        return False
    return True

def main():
    """
    Main function that runs the Streamlit app for the Newsletter Dashboard.
    """
    # Set the title of the app
    st.title("Kalle's Newsletter Dashboard")

    # Cache for processing podcasts
    if 'processed' not in st.session_state:
        st.session_state.processed = {}

    if 'can_process_podcast' not in st.session_state:
        st.session_state.can_process_podcast = True

    # Create a dictionary of available podcast information from JSON files in the current directory
    available_podcast_info = create_dict_from_json_files('.')

    # Left section - Input fields
    st.sidebar.header("Podcast RSS Feeds")

    # Dropdown box to select from available podcast feeds
    st.sidebar.subheader("Available Podcasts Feeds")
    selected_podcast = st.sidebar.selectbox("Select Podcast", options=available_podcast_info.keys())

    if selected_podcast:
        # Get the selected podcast's information from the dictionary
        podcast_info = available_podcast_info[selected_podcast]

        # Right section - Newsletter content
        st.header("Newsletter Content")

        # Render the selected podcast's information
        render_podcast_info(podcast_info)

    # User Input box
    st.sidebar.subheader("Add and Process New Podcast Feed")

    podcast_url = st.sidebar.text_input("Link to RSS Feed")

    if podcast_url:
        # Validate the URL
        if not validators.url(podcast_url):
            st.sidebar.error("Invalid URL", icon="🚨")
            st.session_state.can_process_podcast = False
        else:
            st.success('URL looks good!', icon="✅")
            st.session_state.can_process_podcast = True

    # Button to process the new podcast feed
    process_button = st.sidebar.button("Process Podcast Feed", disabled=not st.session_state.can_process_podcast)
    st.sidebar.markdown("**Note**: Podcast processing can take up to 5 mins, please be patient.")

    if process_button:
        podcast_info = {}
        
        # Optimization if the podcast has already been processed
        # See: https://docs.streamlit.io/library/advanced-features/button-behavior-and-examples#buttons-to-handle-expensive-or-file-writing-processes
        if podcast_url in st.session_state.processed:
            # Get the podcast information from the session state
            podcast_info = st.session_state.processed[podcast_url]
        else:
            # Process the new podcast feed
            with st.spinner("Processing podcast..."):
                try:
                    podcast_info = process_podcast_info(podcast_url)

                    st.session_state.processed[podcast_url] = podcast_info

                    # Celebratory balloons: https://docs.streamlit.io/library/api-reference/status/st.balloons
                    st.balloons()
                except Exception as e:
                    st.error(f"Error processing podcast: {e}")

        # Right section - Newsletter content
        st.header("Newsletter Content")

        # Render the new podcast's information
        render_podcast_info(podcast_info)

def create_dict_from_json_files(folder_path):
    """
    Function that creates a dictionary of podcast information from JSON files in a given folder path.

    Args:
        folder_path (str): The path to the folder containing the JSON files.

    Returns:
        dict: A dictionary of podcast information, with the podcast name as the key and the podcast details as the value.
    """
    json_files = [f for f in os.listdir(folder_path) if f.endswith('.json')]
    data_dict = {}

    for file_name in json_files:
        file_path = os.path.join(folder_path, file_name)
        with open(file_path, 'r') as file:
            podcast_info = json.load(file)
            podcast_name = podcast_info['podcast_details']['podcast_title']
            # Process the file data as needed
            data_dict[podcast_name] = podcast_info

    return data_dict

def process_podcast_info(url):
    """
    Function that processes a given podcast RSS feed URL and retrieves podcast guest information.

    Args:
        url (str): The URL of the podcast RSS feed.

    Returns:
        dict: A dictionary of podcast information, with the podcast details, guest information, and key moments.
    """
    f = modal.Function.lookup("corise-podcast-project", "process_podcast")
    output = f.call(url, '/content/podcast/')
    return output

def render_podcast_info(podcast_info):
    """
    Function that renders the podcast details, guest information, and key moments.

    Args:
        podcast_info (dict): A dictionary of podcast information, with the podcast details, guest information, and key moments.
    """
    # Display the podcast title
    st.subheader("Episode Title")
    st.write(podcast_info['podcast_details']['episode_title'])

    # Display the podcast summary and the cover image in a side-by-side layout
    col1, col2 = st.columns([7, 3])

    with col1:
        # Display the podcast episode summary
        st.subheader("Podcast Episode Summary")
        st.write(podcast_info['podcast_summary'])

    with col2:
        st.image(podcast_info['podcast_details']['episode_image'], caption="Podcast Cover", width=300, use_column_width=True)

    # Display the podcast guest and their details in a side-by-side layout
    col3, col4 = st.columns([3, 7])

    if 'podcast_guest' in podcast_info:
        with col3:
            st.subheader("Podcast Guest")
            st.write(podcast_info['podcast_guest']['name'])

        with col4:
            st.subheader("Podcast Guest Details")
            
            # Makes the guest details section collapsible
            with st.expander("Podcast Guest Search Results"):
                guest_details = podcast_info["podcast_guest"]['summary']
                for detail in guest_details:
                    st.markdown(f"<a href='{detail['link']}' target='_blank'>{detail['title']}</a><br>{detail['snippet']}", unsafe_allow_html=True)
    else:
        with col3:
            st.subheader("Podcast Guest")
            st.write("No guest information available")

    # Display the five key moments
    st.subheader("Key Moments")
    key_moments = podcast_info['podcast_highlights']
    for moment in key_moments.split('\n'):
        st.markdown(
            f"<p style='margin-bottom: 5px;'>{moment}</p>", unsafe_allow_html=True)
        
if __name__ == '__main__':
    main()

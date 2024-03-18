import streamlit as st
import yaml
from streamlit_tags import st_tags

from video_summarizer.backend.configs.configs import params_path
from video_summarizer.frontend.server import format_response, main

st.sidebar.title("ChatGPT Video Summarizer")

st.sidebar.image("./www/Gemini_Generated_Image.jpeg", width=None)
st.sidebar.divider()

top_n = st.sidebar.number_input(
    label="Top N Videos",
    value=2,
    step=1,
    min_value=1,
    max_value=5,
    help="Retrieves this number of video from a channel to summarise",
)

limit_transcript = st.sidebar.number_input(
    label="Limit Transcript",
    value=0.25,
    step=0.1,
    help="Portion of the video transcript to summarise",
)

sort_by = st.sidebar.selectbox(
    label="Sort By",
    options=["Newest", "Popular", "Oldest"],
    help="Criteria to sort channel videos",
)

submit = st.sidebar.button(label="Submit")

urls = st_tags(label="YOUTUBE VIDEOS")
st.write("Enter a list of YouTube channels or videos.")
st.divider()

channels = [
    url
    for url in urls
    if url.strip().lower().startswith("https://www.youtube.com/@")
]

videos = [
    url
    for url in urls
    if url.strip().lower().startswith("https://www.youtube.com/watch?v=")
]

with open(params_path, mode="r") as f:
    endpoint = yaml.safe_load(f).get("endpoint")

if submit:
    if videos or channels:
        data = {
            "channels": channels,
            "videos": videos,
            "limit_transcript": limit_transcript,
            "top_n": top_n,
            "sort_by": sort_by.lower(),
        }

        response = main(endpoint, data)
        result = format_response(response)
        st.markdown("".join(result), unsafe_allow_html=True)

    else:
        st.markdown("Please include at least one video or channel url.")

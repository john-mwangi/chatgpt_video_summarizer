import streamlit as st
from streamlit_tags import st_tags

from video_summarizer.frontend.call_api import format_response, main

videos = st_tags(label="YouTube Videos")
channels = st_tags(label="YouTube Channels")
top_n = st.sidebar.number_input(
    label="Top N Videos", value=2, step=1, min_value=1, max_value=5
)
limit_transcript = st.sidebar.number_input(
    label="Limit Transcript", value=0.25, step=0.1
)
sort_by = st.sidebar.selectbox(
    label="Sort By", options=["Newest", "Popular", "Oldest"]
)
submit = st.sidebar.button(label="Submit")

if submit:
    url = "http://0.0.0.0:12000/api/v1/summarize_video"

    if videos or channels:
        data = {
            "channels": channels,
            "videos": videos,
            "limit_transcript": limit_transcript,
            "top_n": top_n,
            "sort_by": sort_by,
        }

        response = main(url, data)
        result = format_response(response)
        st.markdown("".join(result))
    else:
        st.markdown("Please include at least one video or channel url.")

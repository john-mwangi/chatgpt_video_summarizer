import streamlit as st
import yaml
from streamlit_tags import st_tags

from video_summarizer.backend.configs.config import params_path
from video_summarizer.frontend.server import format_response, main
from video_summarizer.frontend.utils import validate_url

# https://getbootstrap.com/docs/5.0/getting-started/introduction/
css = """<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.0.2/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-EVSTQN3/azprG1Anm3QDgpJLIm9Nao0Yz1ztcQTwFspd3yD65VohhpuuCOmLASjC" crossorigin="anonymous">"""
st.markdown(css, unsafe_allow_html=True)

st.sidebar.title("ChatGPT Video Summarizer")

st.sidebar.image("./www/Gemini_Generated_Image.jpeg", width=None)
st.sidebar.divider()

sort_by = st.sidebar.selectbox(
    label="Sort By",
    options=["Newest", "Popular", "Oldest"],
    help="Criteria to sort channel videos",
)

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

submit = st.sidebar.button(label="Submit")

urls = st_tags(label="### YOUTUBE VIDEOS")
st.write("_Enter a list of YouTube channels or videos._")
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
    endpoint = yaml.safe_load(f)["endpoint"]["url"]

if submit:
    submitted_urls = set(channels + videos)
    url_validations = [validate_url(url) for url in submitted_urls]
    is_valid = False if not url_validations else all(url_validations)

    if not is_valid:
        st.markdown("One of the urls submitted was invalid")

    else:
        data = {
            "channels": channels,
            "videos": videos,
            "limit_transcript": limit_transcript,
            "top_n": top_n,
            "sort_by": sort_by.lower(),
        }

        response = main(endpoint, data)
        result, is_html = format_response(response, return_html=True)
        st.markdown("".join(result), unsafe_allow_html=is_html)

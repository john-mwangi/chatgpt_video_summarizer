# Video Summarizer
## About
This tool uses ChatGPT to summarise a YouTube video by providing either a YouTube channel or the video link.

It will provide a brief 150 word summary of the video as well as the top 5 main points in the video.
The main points are timestamped so that it's easy to navigate the video where
the conversation is taking place. 

This tool as allows one to determine whether to summarise the entire video or
a portion of the video - the first 25% of the video being the default.

## Installation
- Clone this repo
- Set up Mongodb:
  - Create `admin` user with `readWrite` access
  - Create two databases
- Set up Python in a vitual environment and install the Poetry Python package
- Install packages: `poetry install`
## Creating a Mongodb user
```
use summaries
db.createUser(
  {
    user: "admin",
    pwd: passwordPrompt(),  // or cleartext password
    roles: [
       { role: "readWrite", db: "transcripts" },
       { role: "readWrite", db: "summaries" }
    ]
  }
)
```
## Usage
- Run the api: `uvicorn api:app --host 0.0.0.0 --port 12000`
- Enter a channel url or video url to the api
- Video summaries will be saved in the database

## Sample summary
![Sample video summary](./Screenshot.png)

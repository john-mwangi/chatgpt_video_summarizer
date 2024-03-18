import requests


def main(url: str, data: dict):

    headers = {
        "accept": "application/json",
        "Content-Type": "application/json",
    }

    resp = requests.post(url, headers=headers, json=data)
    return resp


def card(video_title, video_url, summary):
    html = f"""
    <div class="card">
        <div class="card-body">
            <h5 class="card-title">{video_title}</h5>
            <h6 class="card-subtitle mb-2 text-muted">{video_url}</h6>
            <p class="card-text">{summary}</p>
            <a href="{video_url}" title="Watch this video on YouTube" class="btn btn-primary"><font color="white">Watch</font></a>
            <a href="#" title="Chat this video with ChatGPT" class="btn btn-primary"><font color="white">Chat</font></a>
        </div>
    </div>
    """
    return html


def format_response(response, return_html: bool = True) -> list[str]:
    result = []
    content = response.json()
    summaries = content.get("data").get("summaries")

    if return_html:
        for summary in summaries:
            for item in summary:

                video_title = item.get("video_title")
                video_url = item.get("video_url")
                video_summary = item.get("summary")
                video_summary = video_summary.replace("\n", "<br>")

                r = card(
                    video_title=video_title,
                    video_url=video_url,
                    summary=video_summary,
                )

                result.append(r)
            result.append("<hr>")
        return result

    else:
        for summary in summaries:
            for item in summary:
                for k, v in item.items():
                    r = f"**{k.title()}**: {v}\n\n"
                    result.append(r)
            result.append("*----END OF SUMMARY----*\n\n")
        return result

import requests


def main(url: str, data: dict):

    headers = {
        "accept": "application/json",
        "Content-Type": "application/json",
    }

    resp = requests.post(
        url,
        headers=headers,
        json=data,
    )

    return resp


def format_response(response) -> list[str]:
    result = []
    content = response.json()
    summaries = content.get("data").get("summaries")
    for summary in summaries:
        for item in summary:
            for k, v in item.items():
                r = f"**{k.title()}**: {v}\n\n"
                result.append(r)
        result.append("*----END OF SUMMARY----*\n\n")
    return result

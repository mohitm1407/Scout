from re import search
from langchain.tools import tool
import requests
import os


def web_search(search_query: str) -> list[dict]:
    """
    Use Google search to find articles related to a spexcific topic .

    Args:
        search_query : the query to be used for search
    """

    url = "https://google.serper.dev/search"
    api_key = os.getenv("SERPER_API_KEY")

    if not api_key:
        raise ValueError("SERPER_API_KEY environment variable is not set")

    payload = {"q": f"{search_query}"}
    headers = {"X-API-KEY": f"{api_key}", "Content-Type": "application/json"}

    response = requests.request("POST", url, headers=headers, json=payload)

    search_responses = response.text
    return search_responses

from re import search
from langchain.tools import tool
import requests


@tool
def web_search(search_query: str, page: int) -> list[dict]:
    """
    Use Google search to find articles related to a spexcific topic .

    Args:
        search_query : the query to be used for search
        page : each page in the search can have upto 10 responses
    """

    url = "https://google.serper.dev/search"

    payload = {"q": f"{search_query}"}
    headers = {"X-API-KEY": "a2d84b54866405455cf19865203ab8ca43403c7f", "Content-Type": "application/json"}

    response = requests.request("POST", url, headers=headers, json=payload)

    return response.text

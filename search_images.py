import requests
from api import *


def search_images(query):
    base_url = "https://serpapi.com/search"
    params = {
        "q": query,
        "tbm": "isch",  # Image Search
        "key": serpapi_api,
    }

    response = requests.get(base_url, params=params)
    data = response.json()

    if "images_results" in data:
        images = data["images_results"]
        if images:
            first_image = images[0]
            return first_image.get("original")

    return None


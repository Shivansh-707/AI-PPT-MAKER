import os
import requests
from dotenv import load_dotenv

load_dotenv()

PEXELS_API_KEY = os.getenv("PEXELS_API_KEY")

def find_image_url(query: str):
    """Search Pexels for a public image URL matching the query."""
    if not PEXELS_API_KEY or not query:
        return None
    try:
        headers = {"Authorization": PEXELS_API_KEY}
        params = {"query": query, "per_page": 1, "orientation": "landscape"}
        response = requests.get(
            "https://api.pexels.com/v1/search",
            headers=headers,
            params=params,
            timeout=5
        )
        data = response.json()
        photos = data.get("photos", [])
        if photos:
            return photos[0]["src"]["large"]
    except Exception as e:
        print(f"Image search failed for '{query}': {e}")
    return None


if __name__ == "__main__":
    url = find_image_url("solar panels on rooftop")
    print(url)

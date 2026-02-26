import os
import requests
from dotenv import load_dotenv

load_dotenv()

GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")


def places_text_search(query: str, limit: int = 5) -> str:
    """Perform a Google Maps Places Text Search and return a simple text summary."""
    if not GOOGLE_MAPS_API_KEY:
        raise ValueError("GOOGLE_MAPS_API_KEY not set in environment")

    url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
    params = {"query": query, "key": GOOGLE_MAPS_API_KEY}
    resp = requests.get(url, params=params, timeout=10)
    resp.raise_for_status()
    data = resp.json()

    results = data.get("results", [])[:limit]
    if not results:
        return "No places found."

    lines = []
    for i, r in enumerate(results, start=1):
        name = r.get("name")
        addr = r.get("formatted_address")
        lines.append(f"{i}. {name} — {addr}")

    return "\n".join(lines)

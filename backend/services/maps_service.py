import os
import requests
from dotenv import load_dotenv

load_dotenv()

GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")

class MapService:

    def google_maps_search(self, query: str):
        """
        Run a Google Maps Places Text Search using a natural language query.
        Example query: 'coffee near University Park MD'
        """
        url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
        print(f"API Query: {query}")
        params = {
            "query": query,
            "key": GOOGLE_MAPS_API_KEY
        }

        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        results = []

        for place in data.get("results", [])[:5]:
            name = place.get("name", "Unknown")
            address = place.get("formatted_address", "Unknown address")
            rating = place.get("rating", "N/A")
            location = place.get("geometry", {}).get("location", {})

            lat = location.get("lat", "N/A")
            lng = location.get("lng", "N/A")

            results.append(f"{name} — {address} — Rating: {rating} — ({lat}, {lng})")

        return "\n".join(results)

map_service = MapService()
import streamlit as st
import folium
from folium import PolyLine, Marker, Popup
from streamlit_folium import st_folium
from geopy.geocoders import Nominatim
from typing import List, Dict, Union

# ========== CONFIGURABLE ==========

MAPTILER_API_KEY = "xi4qTFUetYad8vHNCOVO"  # Replace with your key from https://cloud.maptiler.com/account/keys/
MAPTILER_TILE_URL = f"https://api.maptiler.com/maps/streets/256/{{z}}/{{x}}/{{y}}.png?key={MAPTILER_API_KEY}"

# ========== UTILS ==========

@st.cache_data(show_spinner=False)
def geocode_location(location: str) -> Union[Dict[str, float], None]:
    """Geocode a location name to lat/lon using OpenStreetMap's Nominatim."""
    geolocator = Nominatim(user_agent="vacation-itinerary-map")
    try:
        location_data = geolocator.geocode(location)
        if location_data:
            return {"lat": location_data.latitude, "lon": location_data.longitude}
    except Exception as e:
        st.error(f"Error geocoding '{location}': {e}")
    return None

def get_coordinates(locations: List[Union[str, Dict]]) -> List[Dict]:
    """Ensure all locations are in coordinate form (dict with lat/lon)."""
    coordinates = []
    for loc in locations:
        if isinstance(loc, str):
            coords = geocode_location(loc)
            if coords:
                coords["name"] = loc
                coordinates.append(coords)
        elif isinstance(loc, dict) and "lat" in loc and "lon" in loc:
            coordinates.append(loc)
    return coordinates

def create_itinerary_map(coordinates: List[Dict], zoom_start=6) -> folium.Map:
    """Build the Folium map with route and markers."""
    if not coordinates:
        return None

    first = coordinates[0]
    fmap = folium.Map(
        location=[first["lat"], first["lon"]],
        zoom_start=zoom_start,
        tiles=None
    )

    folium.TileLayer(
        tiles=MAPTILER_TILE_URL,
        attr='MapTiler',
        name='MapTiler',
        control=False
    ).add_to(fmap)

    route = []
    for idx, loc in enumerate(coordinates):
        latlon = (loc["lat"], loc["lon"])
        route.append(latlon)
        popup_text = loc.get("popup", loc.get("name", f"Stop {idx+1}"))
        Marker(
            location=latlon,
            tooltip=f"Stop {idx+1}",
            popup=Popup(popup_text, max_width=300)
        ).add_to(fmap)

    PolyLine(route, color="blue", weight=4, opacity=0.7).add_to(fmap)
    return fmap

# ========== STREAMLIT COMPONENT ==========

def itinerary_map_view(locations: List[Union[str, Dict]], title: str = "Vacation Itinerary Map"):
    st.subheader(title)

    coords = get_coordinates(locations)
    if not coords:
        st.warning("No valid locations to show on map.")
        return

    fmap = create_itinerary_map(coords)
    if fmap:
        st_data = st_folium(fmap, width=800, height=500)

# ========== EXAMPLE USAGE ==========

if __name__ == "__main__":
    st.title("📍 Vacation Route Planner")
    sample_itinerary = [
        {"name": "Havana, Cuba", "popup": "Day 1: Arrival in Havana"},
        "Cienfuegos, Cuba",
        {"name": "Trinidad, Cuba", "popup": "Day 3: Explore Trinidad"},
        "Viñales, Cuba"
    ]
    itinerary_map_view(sample_itinerary)

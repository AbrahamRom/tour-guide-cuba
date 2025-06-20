import streamlit as st
import folium
from folium import PolyLine, Marker, Popup
from streamlit_folium import st_folium
from geopy.geocoders import Nominatim
from typing import List, Dict, Union
import re

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

def limpiar_nombre(nombre: str) -> str:
    """
    Limpia el nombre del hotel quitando estrellas, paréntesis y caracteres especiales.
    """
    # Elimina estrellas y paréntesis
    nombre = re.sub(r"\(\d+★\)", "", nombre)
    nombre = re.sub(r"[\(\)★]", "", nombre)
    nombre = nombre.strip()
    return nombre

def enriquecer_nombre(nombre: str) -> str:
    """
    Añade 'Cuba' al nombre si no está presente.
    """
    if "Cuba" not in nombre:
        return f"{nombre}, Cuba"
    return nombre

def get_coordinates(locations: List[Union[str, Dict]]) -> List[Dict]:
    """Ensure all locations are in coordinate form (dict with lat/lon)."""
    coordinates = []
    for loc in locations:
        if isinstance(loc, str):
            # Intenta varias variantes del nombre
            variantes = [loc, limpiar_nombre(loc), enriquecer_nombre(limpiar_nombre(loc))]
            coords = None
            for variante in variantes:
                coords = geocode_location(variante)
                if coords:
                    coords["name"] = variante
                    break
            if coords:
                coordinates.append(coords)
        elif isinstance(loc, dict):
            nombre = loc.get("name", "")
            popup = loc.get("popup", "")
            # Intenta varias variantes del nombre
            variantes = [nombre, limpiar_nombre(nombre), enriquecer_nombre(limpiar_nombre(nombre))]
            coords = None
            for variante in variantes:
                coords = geocode_location(variante)
                if coords:
                    coords["name"] = variante
                    coords["popup"] = popup
                    break
            if coords:
                coordinates.append(coords)
    return coordinates

def create_itinerary_map(coordinates: List[Dict], zoom_start=6) -> folium.Map:
    """Build the Folium map with route and markers."""
    if not coordinates:
        # Coordenadas de La Habana por defecto
        coordinates = [{"lat": 23.1136, "lon": -82.3666, "name": "La Habana, Cuba", "popup": "La Habana (por defecto)"}]

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

    if len(route) > 1:
        PolyLine(route, color="blue", weight=4, opacity=0.7).add_to(fmap)
    return fmap

# ========== STREAMLIT COMPONENT ==========

def itinerary_map_view(locations: List[Union[str, Dict]], title: str = "Vacation Itinerary Map"):
    st.subheader(title)

    coords = get_coordinates(locations)
    fmap = create_itinerary_map(coords)
    if not coords:
        st.info("No se encontraron ubicaciones válidas. Mostrando La Habana por defecto.")
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

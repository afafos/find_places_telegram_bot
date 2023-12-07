import requests
import math
from api import *

API_KEY = mapquest_api


# Function to calculate the distance between two coordinates
def calculate_distance(lat1, lon1, lat2, lon2):
    # Radius of the Earth in kilometers
    radius = 6371.0

    # Converting coordinates from degrees to radians
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)

    # Difference between coordinates
    dlon = lon2_rad - lon1_rad
    dlat = lat2_rad - lat1_rad

    # Calculate the distance using the Gaversine formula
    a = math.sin(dlat / 2) ** 2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    distance = radius * c
    return distance


# Function to get coordinates (latitude and longitude) from an address
def get_coordinates_by_address(address):
    base_url = "http://www.mapquestapi.com/geocoding/v1/address"
    params = {"key": API_KEY, "location": address}
    response = requests.get(base_url, params=params)
    data1 = response.json()

    if data1["results"]:
        location = data1["results"][0]["locations"][0]
        lat = location["latLng"]["lat"]
        lng = location["latLng"]["lng"]
        return lat, lng
    else:
        return None


# Function for building a route between two points
def get_directions(start, end):
    start_coords = get_coordinates_by_address(start)
    end_coords = get_coordinates_by_address(end)

    if start_coords and end_coords:
        base_url = "http://www.mapquestapi.com/directions/v2/route"
        params = {
            "key": API_KEY,
            "from": f"{start_coords[0]},{start_coords[1]}",
            "to": f"{end_coords[0]},{end_coords[1]}"
        }
        response = requests.get(base_url, params=params)
        data = response.json()

        if data["route"]:
            directions = data["route"]["legs"][0]["maneuvers"]
            direction_strings = [step["narrative"] for step in directions]
            directions_str = '\n'.join(direction_strings)
            return directions_str
        else:
            return "Route not found."

    else:
        return "Could not determine coordinates for the specified addresses."


# Function to get map scale based on distance
def get_map_zoom(distance):
    zoom = 10
    distance_ch = distance
    if distance_ch >= 31:
        while distance_ch >= 31:
            distance_ch /= 2
            zoom -= 1

    else:
        while distance_ch <= 31:
            distance_ch *= 2
            zoom += 1

    return zoom


# Function to get a static map with start and end points marked
def get_static_map(start, end, zoom):
    start_coords = get_coordinates_by_address(start)
    end_coords = get_coordinates_by_address(end)

    if start_coords and end_coords:
        base_url = "http://www.mapquestapi.com/staticmap/v5/map"
        params = {
            "key": API_KEY,
            "size": "600,600",  # Card size (width x height)
            "zoom": zoom,  # Map scale
            "locations": f"{start_coords[0]},{start_coords[1]}|marker-start||{end_coords[0]},{end_coords[1]}|marker-end|",
        }

        response = requests.get(base_url, params=params)

        if response.status_code == 200:
            with open("map.jpg", "wb") as file:
                file.write(response.content)
            print("The map with the starting and ending points marked is saved in a file map.jpg")

        else:
            print("Failed to receive map.")
    else:
        print("Could not determine coordinates for the specified addresses.")

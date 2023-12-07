import re
import json
import os


# Function to save data as JSON
def save_place_data(place_data, name):
    name = re.sub(r'[\/:*?"<>|]', '_', name)
    filename = f"{name}.json"
    with open(filename, "w") as file:
        json.dump(place_data, file, indent=4)


# Function to remove old JSON files
def delete_old_json_files():
    for filename in os.listdir():
        if filename.endswith(".json"):
            os.remove(filename)

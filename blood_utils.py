import json
from geopy.geocoders import Nominatim
from geopy.distance import geodesic

# Convert locality to coordinates in Jaipur
def get_coordinates(locality):
    geolocator = Nominatim(user_agent="blood_locator")
    full_location = f"{locality}, Jaipur, India"
    loc = geolocator.geocode(full_location)
    if loc:
        return (loc.latitude, loc.longitude)
    return None

# Save a new entry with coordinates
def save_entry(entry):
    coords = get_coordinates(entry["location"])
    if coords is None:
        print("❌ Could not locate the area. Please try a known Jaipur locality.")
        return False

    entry["coordinates"] = coords
    with open("blood_data.json", "r+") as file:
        data = json.load(file)
        data.append(entry)
        file.seek(0)
        json.dump(data, file, indent=4)
    return True

# Check blood group validity
def is_valid_blood_group(group):
    return group.upper() in ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]

# Find closest matching entries
def find_match(entry, compatible_groups=None):
    with open("blood_data.json", "r") as file:
        data = json.load(file)

    if "coordinates" not in entry or entry["coordinates"] is None:
        return []

    opposite_type = "offer" if entry["type"] == "request" else "request"
    matches = []

    # If compatible_groups is not provided, use the entry's blood group
    if compatible_groups is None:
        compatible_groups = [entry["blood_group"].upper()]
    else:
        compatible_groups = [bg.upper() for bg in compatible_groups]

    for item in data:
        if (
            item["type"] == opposite_type and
            item["blood_group"].upper() in compatible_groups and
            item.get("coordinates")
        ):
            dist = geodesic(entry["coordinates"], tuple(item["coordinates"])).km
            item["distance"] = round(dist, 2)
            matches.append(item)

    matches.sort(key=lambda x: x["distance"])
    return matches
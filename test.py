import pyairbnb
import json
# Define search parameters
currency = "MXN"  # Currency for the search
check_in = "2025-04-01"  # Check-in date
check_out = "2025-04-04"  # Check-out date
ne_lat = 38.02478722891261  # North-East latitude
ne_long = -121.78973354593924  # North-East longitude
sw_lat = 37.10169182888774  # South-West latitude
sw_long = -122.73730428910152  # South-West longitude
zoom_value = 2  # Zoom level for the map
price_min = 3000
price_max = 0
place_type = "" #or "Entire home/apt"
# Search listings within specified coordinates and date range
search_results = pyairbnb.search_all(check_in, check_out, ne_lat, ne_long, sw_lat, sw_long, zoom_value, currency, place_type, price_min, price_max,  "")

# Save the search results as a JSON file
with open('search_results.json', 'w', encoding='utf-8') as f:
    f.write(json.dumps(search_results))  # Convert results to JSON and write to file
import pyairbnb
import json

# Define search parameters
currency = "USD"
check_in = "2025-01-13"
check_out = "2025-01-17"
ne_lat = 26.244992525492258
ne_long = -80.20554283078371
sw_lat = 26.052735877248157
sw_long = -80.39148365866907
zoom_value = 12

# Search listings within specified coordinates and date range
search_results = pyairbnb.search_all(check_in, check_out, ne_lat, ne_long, sw_lat, sw_long, zoom_value, currency, "")

# Save the search results as a JSON file
with open('search_results.json', 'w', encoding='utf-8') as f:
    f.write(json.dumps(search_results))  # Convert results to JSON and write to file


api_key = pyairbnb.get_api_key("")

experiences = pyairbnb.search_experience("Estados Unidos", check_in, check_out, currency,api_key, "")

with open('experiences.json', 'w', encoding='utf-8') as f:
    f.write(json.dumps(experiences))  # Convert results to JSON and write to file

listings = pyairbnb.get_listings_from_user(71501403,api_key,"")

with open('listings.json', 'w', encoding='utf-8') as f:
    f.write(json.dumps(listings))  # Convert results to JSON and write to file


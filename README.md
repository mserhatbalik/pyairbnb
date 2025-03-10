# Airbnb scraper in Python

## Overview
This project is an open-source tool developed in Python for extracting product information from Airbnb. It's designed to be easy to use, making it an ideal solution for developers looking for Airbnb product data.

## Features
- Extract prices, available dates, reviews, host details and others
- Full search support
- Extracts detailed product information from Airbnb
- Implemented in Python just because it's popular
- Easy to integrate with existing Python projects

## Legacy
- This was a project first implemented on:[https://github.com/johnbalvin/pybnb](https://github.com/johnbalvin/pybnb) but was moved to [https://github.com/johnbalvin/pyairbnb](https://github.com/johnbalvin/pyairbnb)
to match the name with pip name

## Important
- With the new airbnb changes, if you want to get the price from a room url you need to specify the date range
the date range should be on the format year-month-day, if you leave the date range empty, you will get the details but not the price


### Install

```bash
$ pip install pyairbnb
```
## Examples

### Example for Searching Listings

```python
import pyairbnb
import json

# Define search parameters
currency = "MXN"  # Currency for the search
check_in = "2025-02-01"  # Check-in date
check_out = "2025-02-04"  # Check-out date
ne_lat = -1.03866277790021  # North-East latitude
ne_long = -77.53091734683608  # North-East longitude
sw_lat = -1.1225978433925647  # South-West latitude
sw_long = -77.59713412765507  # South-West longitude
zoom_value = 2  # Zoom level for the map

# Search listings within specified coordinates and date range
search_results = pyairbnb.search_all(check_in, check_out, ne_lat, ne_long, sw_lat, sw_long, zoom_value, currency, "")

# Save the search results as a JSON file
with open('search_results.json', 'w', encoding='utf-8') as f:
    f.write(json.dumps(search_results))  # Convert results to JSON and write to file
```

### Retrieving Details for Listings

### Getting price
```python
import pyairbnb
import json
room_url="https://www.airbnb.com/rooms/30931885"
check_in = "2025-04-10"
check_out = "2025-04-12"
proxy_url = ""  # Proxy URL (if needed)
data, price_input, cookies = pyairbnb.get_metadata_from_url(room_url, proxy_url)
product_id = price_input["product_id"]
api_key = price_input["api_key"]
currency = "USD"
data = pyairbnb.get_price(product_id, price_input["impression_id"], api_key, currency, cookies,
            check_in, check_out, proxy_url)

with open('price.json', 'w', encoding='utf-8') as f:
    f.write(json.dumps(data))
```


### Getting listings from user id
```Python
import pyairbnb
import json
host_id = 0
api_key = pyairbnb.get_api_key("")
listings = pyairbnb.get_listings_from_user(host_id,api_key,"")
with open('listings.json', 'w', encoding='utf-8') as f:
    f.write(json.dumps(listings))
```

### Getting experiences by just taking the first autocompletions that you would normally do manually on the website
```Python
import pyairbnb
import json
check_in = "2025-04-10"
check_out = "2025-04-12"
currency = "EUR"
user_input_text = "Estados Unidos"
locale = "es"
proxy_url = ""  # Proxy URL (if needed)
api_key = pyairbnb.get_api_key("")
experiences = pyairbnb.experience_search(user_input_text, currency, locale, check_in, check_out, api_key, proxy_url)
with open('experiences.json', 'w', encoding='utf-8') as f:
    f.write(json.dumps(experiences))
```

### Getting experiences by first getting the autocompletions
```Python
import pyairbnb
import json
check_in = "2025-03-06"
check_out = "2025-03-10"
currency = "USD"
user_input_text = "cuenca"
locale = "pt"
proxy_url = ""  # Proxy URL (if needed)
api_key = pyairbnb.get_api_key("")
markets_data = pyairbnb.get_markets(currency,locale,api_key,proxy_url)
markets = pyairbnb.get_nested_value(markets_data,"user_markets", [])
if len(markets)==0:
    raise Exception("markets are empty")
config_token = pyairbnb.get_nested_value(markets[0],"satori_parameters", "")
country_code = pyairbnb.get_nested_value(markets[0],"country_code", "")
if config_token=="" or country_code=="":
    raise Exception("config_token or country_code are empty")
place_ids_results = pyairbnb.get_places_ids(country_code, user_input_text, currency, locale, config_token, api_key, proxy_url)
if len(place_ids_results)==0:
    raise Exception("empty places ids")
place_id = pyairbnb.get_nested_value(place_ids_results[0],"location.google_place_id", "")
location_name = pyairbnb.get_nested_value(place_ids_results[0],"location.location_name", "")
if place_id=="" or location_name=="":
    raise Exception("place_id or location_name are empty")
[result,cursor] = pyairbnb.experience_search_by_place_id("", place_id, location_name, currency, locale, check_in, check_out, api_key, proxy_url)
while cursor!="":
    [result_tmp,cursor] = pyairbnb.experience_search_by_place_id(cursor, place_id, location_name, currency, locale, check_in, check_out, api_key, proxy_url)
    if len(result_tmp)==0:
        break
    result = result + result_tmp
with open('experiences.json', 'w', encoding='utf-8') as f:
    f.write(json.dumps(result))
```

### Getting available/unavailable homes along with metadata
```Python
import pyairbnb
import json

# Define listing URL and parameters
room_url = "https://www.airbnb.com/rooms/1029961446117217643"  # Listing URL
currency = "USD"  # Currency for the listing details

# Retrieve listing details without including the price information (no check-in/check-out dates)
data = pyairbnb.get_details(room_url=room_url, currency=currency)

# Save the retrieved details to a JSON file
with open('details_data.json', 'w', encoding='utf-8') as f:
    f.write(json.dumps(data))  # Convert the data to JSON and save it
```

#### Retrieve Details Using Room ID with Proxy
You can also use `get_details` with a room ID and an optional proxy.

```python
import pyairbnb
from urllib.parse import urlparse
import json

# Define listing parameters
room_id = 18039593  # Listing room ID
currency = "MXN"  # Currency for the listing details
proxy_url = ""  # Proxy URL (if needed)

# Retrieve listing details by room ID with a proxy
data = pyairbnb.get_details(room_id=room_id, currency=currency, proxy_url=proxy_url)

# Save the retrieved details to a JSON file
with open('details_data.json', 'w', encoding='utf-8') as f:
    f.write(json.dumps(data))  # Convert the data to JSON and save it
```

### Retrieve Reviews for a Listing
Use `get_reviews` to extract reviews and metadata for a specific listing.

```python
import pyairbnb
import json

# Define listing URL and proxy URL
room_url = "https://www.airbnb.com/rooms/30931885"  # Listing URL
proxy_url = ""  # Proxy URL (if needed)

# Retrieve reviews for the specified listing
reviews_data = pyairbnb.get_reviews(room_url, proxy_url)

# Save the reviews data to a JSON file
with open('reviews.json', 'w', encoding='utf-8') as f:
    f.write(json.dumps(reviews_data))  # Extract reviews and save them to a file
```

### Retrieve Availability for a Listing
The `get_calendar` function provides availability information for specified listings.

```python
import pyairbnb
import json

# Define listing parameters
room_id = "44590727"  # Listing room ID
proxy_url = ""  # Proxy URL (if needed)

# Retrieve availability for the specified listing
calendar_data = pyairbnb.get_calendar(room_id, "", proxy_url)

# Save the calendar data (availability) to a JSON file
with open('calendar.json', 'w', encoding='utf-8') as f:
    f.write(json.dumps(calendar_data))  # Extract calendar data and save it to a file
```

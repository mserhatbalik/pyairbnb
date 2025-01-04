# Airbnb scraper in Python

## Overview
This project is an open-source tool developed in Python for extracting product information from Airbnb. It's designed to be easy to use, making it an ideal solution for developers looking for Airbnb product data.

## Features
- Extract prices, available dates, reviews and others
- Full search support
- Extracts detailed product information from Airbnb
- Implemented in Python just because it's popular
- Easy to integrate with existing Python projects
- The code is optimize to work on this format: ```https://www.airbnb.com/rooms/[room_id]```

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

```Python
import pyairbnb
import json
currency="MXN"
check_in = "2025-02-01"
check_out = "2025-02-04"
ne_lat = -1.03866277790021
ne_long = -77.53091734683608
sw_lat = -1.1225978433925647
sw_long = -77.59713412765507
zoom_value = 2
search_results = pyairbnb.search_all(check_in,check_out,ne_lat,ne_long,sw_lat,sw_long,zoom_value, currency,"")
details_data = []
progress = 1
with open('search_results.json', 'w', encoding='utf-8') as f:
    f.write(json.dumps(search_results))
for result in search_results[:10]:
    data = pyairbnb.get_details_from_id(result["room_id"],currency,check_in,check_out,"")
    details_data.append(data)
    print("len results: ",progress, len(search_results))
    progress=progress+1

with open('details_data_json.json', 'w', encoding='utf-8') as f:
    f.write(json.dumps(details_data))
```

### Example for getting prices, avaiable dates, reviews and other metadata

### Getting the reviews, along with metadata
```Python
import pyairbnb
import json
room_url="https://www.airbnb.com/rooms/30931885"
data = pyairbnb.get_reviews(room_url,"")
with open('reviews.json', 'w', encoding='utf-8') as f:
    f.write(json.dumps(data["reviews"]))
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

### Getting experience from user id
```Python
import pyairbnb
import json
check_in = "2025-04-10"
check_out = "2025-04-12"
api_key = pyairbnb.get_api_key("")
experiences = pyairbnb.search_experience("Estados Unidos",check_in,check_out,"EUR",api_key,"")
with open('experiences.json', 'w', encoding='utf-8') as f:
    f.write(json.dumps(experiences))
```

### Getting available/unavailable, along with metadata
```Python
import pyairbnb
import json
room_url="https://www.airbnb.com/rooms/44590727"
calendar = pyairbnb.get_calendar(room_url,"")
with open('calendar.json', 'w', encoding='utf-8') as f:
    f.write(json.dumps(calendar["calendar"]))
```

### if you want to get the price you need to send the check in and check out date(this is a requirement on airbn itself)
```Python
import pyairbnb
import json
room_url="https://www.airbnb.com/rooms/43198150"
currency="USD"
check_in = "2025-01-02"
check_out = "2025-01-04"
data = pyairbnb.get_details_from_url(room_url,currency,check_in,check_out,"")
with open('details_data_json.json', 'w', encoding='utf-8') as f:
    f.write(json.dumps(data))
```


### example for getting details and NOT price
### if you won't want the price, you can just leave it empty
```Python
import pyairbnb
import json
room_url="https://www.airbnb.com/rooms/1029961446117217643"
currency="USD"
check_in = ""
check_out = ""
data = pyairbnb.get_details_from_url(room_url,currency,check_in,check_out,"")
with open('details_data_json.json', 'w', encoding='utf-8') as f:
    f.write(json.dumps(data))
```

```Python
import pyairbnb
import json
room_id=18039593#the room id
currency="MXN"
check_in = ""
check_out = ""
proxy_url = pyairbnb.parse_proxy("[IP or domain]","[port]","[user name]","[password]")
data = pyairbnb.get_details_from_id(room_id,currency,check_in,check_out,proxy_url)
with open('details_data_json.json', 'w', encoding='utf-8') as f:
    f.write(json.dumps(data))
```

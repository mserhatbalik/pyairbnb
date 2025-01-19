import pyairbnb
import json
check_in = "2025-03-06"
check_out = "2025-03-10"
currency = "USD"
user_input_text = "quito"
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
from curl_cffi import requests
from urllib.parse import urlencode
import pyairbnb.utils as utils
import uuid
import json

ep = "https://www.airbnb.es/api/v3/ExperiencesSearch/1689447deee9494717e151cae73d20ce78fdcb3bac07e1aeae144a1bfe3d1b0a"

def search(location: str, check_in:str, check_out:str, currency:str, api_key:str, proxy_url:str):
    query_params = {
        "operationName": "ExperiencesSearch",
        "locale": "en",
        "currency": currency,
    }
    url_parsed = f"{ep}?{urlencode(query_params)}"
    rawParams=[
        {"filterName":"cdnCacheSafe","filterValues":["false"]},
        {"filterName":"checkin","filterValues":[check_in]},
        {"filterName":"checkout","filterValues":[check_out]},
        {"filterName":"datePickerType","filterValues":["calendar"]},
        {"filterName":"federatedSearchSessionId","filterValues":[str(uuid.uuid4())]},
        {"filterName":"flexibleTripLengths","filterValues":["one_week"]},
        {"filterName":"isOnlineExperiences","filterValues":["false"]},
        {"filterName":"itemsPerGrid","filterValues":["24"]},
        {"filterName":"location","filterValues":[location]},
        {"filterName":"monthlyEndDate","filterValues":["2025-05-01"]},
        {"filterName":"monthlyLength","filterValues":["3"]},
        {"filterName":"monthlyStartDate","filterValues":["2025-02-01"]},
        {"filterName":"placeId","filterValues":["ChIJCzYy5IS16lQRQrfeQ5K5Oxw"]},
        {"filterName":"query","filterValues":[location]},
        {"filterName":"rankMode","filterValues":["default"]},
        {"filterName":"refinementPaths","filterValues":["/experiences"]},
        {"filterName":"screenSize","filterValues":["large"]},
        {"filterName":"searchType","filterValues":["filter_change"]},
        {"filterName":"source","filterValues":["structured_search_input_header"]},
        {"filterName":"tabId","filterValues":["experience_tab"]},
        {"filterName":"version","filterValues":["1.8.3"]}
    ]
    inputData = {
        "operationName":"ExperiencesSearch",
        "extensions":{
            "persistedQuery": {
                "version": 1,
                "sha256Hash": "1689447deee9494717e151cae73d20ce78fdcb3bac07e1aeae144a1bfe3d1b0a",
            },
        },
        "variables":{
            "isLeanTreatment": False,
            "experiencesSearchRequest": {
                "metadataOnly": False,
                "rawParams": rawParams,
                "searchType": "filter_change",
                "source": "structured_search_input_header",
                "treatmentFlags":[
                    "stays_search_rehydration_treatment_desktop",
                    "stays_search_rehydration_treatment_moweb",
                    "experiences_search_feed_only_treatment",
                ]
            },
        },
    }
    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "Accept-Language": "en",
        "Cache-Control": "no-cache",
        "content-type": "application/json",
        "Connection": "close",
        "Pragma": "no-cache",
        "Sec-Ch-Ua": '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
        "Sec-Ch-Ua-Mobile": "?0",
        "X-Airbnb-Api-Key": api_key,
        "Sec-Ch-Ua-Platform": '"Windows"',
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    proxies = {}
    if proxy_url:
        proxies = {"http": proxy_url, "https": proxy_url}
    response = requests.post(url_parsed, json = inputData, headers=headers, proxies=proxies,  impersonate="chrome110")
    data = response.json()
    to_return=utils.get_nested_value(data,"data.presentation.experiencesSearch.results.searchResults",{})
    return to_return
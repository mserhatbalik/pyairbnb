import pyairbnb
import json
import time
import pandas as pd
import os
from typing import List, Dict, Any

# --- Configuration ---
# Define the geographic area to be scraped
sw_long_orig = 28.97
sw_lat_orig = 41.03
ne_long_orig = 28.98
ne_lat_orig = 41.04
# Initial grid size for dividing the main area
grid_size = 4
# Output file names
output_excel_file = 'istanbul_listings_analysis.xlsx'
output_json_file = 'search_results_all_final.json'
output_urls_file = 'airbnb_all_listings_final.txt'

# --- Conversion Logic (from converter.py) ---

def process_listing_data(listing: Dict[str, Any]) -> Dict[str, Any]:
    """
    Flattens a single listing's JSON object into a flat dictionary.
    This is necessary to convert the nested JSON structure into a 2D Excel table.

    Args:
        listing (dict): A dictionary representing a single property listing.

    Returns:
        dict: A flattened dictionary containing all the key information.
    """
    # Use .get() to safely access keys that might be missing in some records
    price_info = listing.get('price', {})
    price_unit = price_info.get('unit', {})
    rating_info = listing.get('rating', {})
    room_id = listing.get('room_id')

    # Construct the full URL for the listing
    listing_url = f"https://www.airbnb.com/rooms/{room_id}" if room_id else "N/A"

    # Join all price breakdown descriptions into a single string
    price_breakdown_desc = ""
    if price_info.get('break_down'):
        price_breakdown_desc = " | ".join([item.get('description', '') for item in price_info.get('break_down', [])])

    return {
        'room_id': room_id,
        'listing_url': listing_url,
        'category': listing.get('category'),
        'name': listing.get('name'),
        'title': listing.get('title'),
        'rating_value': rating_info.get('value'),
        'rating_review_count': rating_info.get('reviewCount'),
        'is_superhost': 'SUPERHOST' in listing.get('badges', []),
        'is_guest_favorite': 'GUEST_FAVORITE' in listing.get('badges', []),
        'latitude': listing.get('coordinates', {}).get('latitude'),
        'longitude': listing.get('coordinates', {}).get('longitude'),
        'price_unit_qualifier': price_unit.get('qualifier'),
        'price_unit_currency_symbol': price_unit.get('curency_symbol'), # Note: Typo 'curency_symbol' is in original data
        'price_unit_original_amount': price_unit.get('amount'),
        'price_unit_discounted_amount': price_unit.get('discount'),
        'price_breakdown_summary': price_breakdown_desc,
        'first_image_url': listing.get('images', [{}])[0].get('url') # Get the URL of the first image
    }

def convert_data_to_excel(listings_data: List[Dict[str, Any]], output_excel_path: str):
    """
    Processes the scraped listing data and saves it as an Excel file.

    Args:
        listings_data (List[Dict[str, Any]]): A list of dictionary objects, where each dictionary is a scraped listing.
        output_excel_path (str): The path where the output Excel file will be saved.
    """
    print("\n--- Starting Data Conversion to Excel ---")
    try:
        # Process each listing in the data using a list comprehension
        processed_data = [process_listing_data(listing) for listing in listings_data]

        # Create a pandas DataFrame from the list of processed dictionaries
        df = pd.DataFrame(processed_data)
        print(f"Successfully converted {len(df)} listings into a DataFrame.")

        # Save the DataFrame to an Excel file
        df.to_excel(output_excel_path, index=False, engine='openpyxl')
        print(f"✅ Success! Data has been exported to '{output_excel_path}'.")

    except Exception as e:
        print(f"❌ An unexpected error occurred during Excel conversion: {e}")


# --- Main Execution Block (Combined Logic) ---

def main():
    """
    Main function to run the scraping and conversion process.
    """
    # --- Part 1: Scraping Logic (from scrape_airbnb.py) ---
    print("--- Starting Airbnb Scrape ---")
    
    # Generate bounding boxes for the grid search
    bounding_boxes = []
    lat_step = (ne_lat_orig - sw_lat_orig) / grid_size
    long_step = (ne_long_orig - sw_long_orig) / grid_size

    for i in range(grid_size):
        for j in range(grid_size):
            sw_lat = sw_lat_orig + i * lat_step
            sw_long = sw_long_orig + j * long_step
            ne_lat = sw_lat_orig + (i + 1) * lat_step
            ne_long = sw_long_orig + (j + 1) * long_step
            
            # This logic handles the subdivision of a dense area, as in the original script
            if i == 3 and j == 1:
                sub_grid_size = 2
                sub_lat_step = (ne_lat - sw_lat) / sub_grid_size
                sub_long_step = (ne_long - sw_long) / sub_grid_size
                for sub_i in range(sub_grid_size):
                    for sub_j in range(sub_grid_size):
                        bounding_boxes.append({
                            "sw_lat": sw_lat + sub_i * sub_lat_step,
                            "sw_long": sw_long + sub_j * sub_long_step,
                            "ne_lat": sw_lat + (sub_i + 1) * sub_lat_step,
                            "ne_long": sw_long + (sub_j + 1) * sub_long_step,
                            "name": f"Area_{i+1}_{j+1}_Sub_{sub_i+1}_{sub_j+1}"
                        })
            else:
                bounding_boxes.append({
                    "sw_lat": sw_lat, "sw_long": sw_long, "ne_lat": ne_lat, "ne_long": ne_long,
                    "name": f"Area_{i+1}_{j+1}"
                })

    all_listings = {} # Using a dictionary for automatic de-duplication
    check_in, check_out, currency, language = "", "", "USD", "en"

    for i, box in enumerate(bounding_boxes):
        print(f"\nSearching in area {i+1}/{len(bounding_boxes)} ({box['name']})...")
        try:
            search_results = pyairbnb.search_all(
                check_in=check_in, check_out=check_out, ne_lat=box["ne_lat"], ne_long=box["ne_long"],
                sw_lat=box["sw_lat"], sw_long=box["sw_long"], zoom_value=17, price_min=0, price_max=0,
                place_type="", amenities=[], currency=currency, language=language, proxy_url=""
            )
            print(f"Found {len(search_results)} listings in this area.")
            for listing in search_results:
                all_listings[listing['room_id']] = listing

            if i < len(bounding_boxes) - 1:
                time.sleep(3) # A small delay to avoid overwhelming the server

        except Exception as e:
            print(f"❌ An error occurred while searching area {box['name']}: {e}")

    unique_listings = list(all_listings.values())
    print(f"\n>>> Scrape complete. Found a total of {len(unique_listings)} unique listings across all {len(bounding_boxes)} areas. <<<")

    # --- Part 2: Saving and Converting the Data ---
    
    # Save the raw JSON data (optional, but good for backup)
    try:
        with open(output_json_file, 'w', encoding='utf-8') as f:
            json.dump(unique_listings, f, ensure_ascii=False, indent=4)
        print(f"\n✅ Full raw data saved to '{output_json_file}'")
    except Exception as e:
        print(f"❌ Error saving JSON file: {e}")

    # Save the listing URLs
    try:
        listing_urls = [f"https://www.airbnb.com/rooms/{listing['room_id']}" for listing in unique_listings]
        with open(output_urls_file, 'w') as f:
            for url in listing_urls:
                f.write(f"{url}\n")
        print(f"✅ All unique listing URLs saved to '{output_urls_file}'")
    except Exception as e:
        print(f"❌ Error saving URLs file: {e}")

    # Directly call the conversion function with the in-memory data
    if unique_listings:
        convert_data_to_excel(unique_listings, output_excel_file)

    print("\n🎉 All done!")


if __name__ == "__main__":
    main()
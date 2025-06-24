# USAGE: python scrape_bulk_listings.py --file listings.txt

import pyairbnb
import json
import argparse
import re
import pandas as pd
import time
import random
from typing import Dict, Any, List

def save_as_excel(data: Dict[str, Any], filename: str, url: str):
    """
    Processes the detailed listing data and saves it as a multi-sheet Excel file.

    Args:
        data (Dict[str, Any]): The scraped data from pyairbnb.
        filename (str): The path for the output Excel file.
        url (str): The original URL for inclusion in the summary.
    """
    print(f"  Creating Excel report at '{filename}'...")
    try:
        with pd.ExcelWriter(filename, engine='openpyxl') as writer:
            # --- 1. Summary Sheet ---
            summary_data = {
                "Field": [
                    "Listing URL", "Title", "Description", "Room Type", "Person Capacity",
                    "Is Superhost", "Is Guest Favorite", "Latitude", "Longitude",
                    "Overall Rating", "Guest Satisfaction", "Accuracy Rating", "Check-in Rating",
                    "Cleanliness Rating", "Communication Rating", "Location Rating", "Value Rating",
                    "Review Count", "Host Name", "Host Joined On"
                ],
                "Value": [
                    url,
                    data.get('title', 'N/A'),
                    data.get('description', 'N/A'),
                    data.get('room_type', 'N/A'),
                    data.get('person_capacity', 'N/A'),
                    data.get('is_super_host', 'N/A'),
                    data.get('is_guest_favorite', 'N/A'),
                    data.get('coordinates', {}).get('latitude', 'N/A'),
                    data.get('coordinates', {}).get('longitude', 'N/A'),
                    data.get('rating', {}).get('value', 'N/A'),
                    data.get('rating', {}).get('guest_satisfaction', 'N/A'),
                    data.get('rating', {}).get('accuracy', 'N/A'),
                    data.get('rating', {}).get('checking', 'N/A'),
                    data.get('rating', {}).get('cleanliness', 'N/A'),
                    data.get('rating', {}).get('communication', 'N/A'),
                    data.get('rating', {}).get('location', 'N/A'),
                    data.get('rating', {}).get('value', 'N/A'),
                    data.get('rating', {}).get('review_count', 'N/A'),
                    data.get('host', {}).get('name', 'N/A'),
                    data.get('host', {}).get('joined_on', 'N/A'),
                ]
            }
            pd.DataFrame(summary_data).to_excel(writer, sheet_name='Summary', index=False)

            # --- 2. Reviews Sheet ---
            if data.get('reviews'):
                reviews_df = pd.json_normalize(data['reviews'])
                review_cols = {
                    'createdAt': 'Date', 'comments': 'Comment', 'localizedDate': 'Localized Date',
                    'reviewer.firstName': 'Reviewer Name', 'response': 'Host Response'
                }
                reviews_df = reviews_df[[col for col in review_cols.keys() if col in reviews_df.columns]].rename(columns=review_cols)
                reviews_df.to_excel(writer, sheet_name='Reviews', index=False)

            # --- 3. Calendar & Pricing Sheet ---
            if data.get('calendar'):
                calendar_list = []
                for month_data in data['calendar']:
                    for day_data in month_data.get('days', []):
                        calendar_list.append({
                            'Date': day_data.get('date'), 'Available': day_data.get('available'),
                            'Price': day_data.get('price', {}).get('nativePrice'),
                            'Min Nights': day_data.get('minNights'), 'Max Nights': day_data.get('maxNights'),
                        })
                pd.DataFrame(calendar_list).to_excel(writer, sheet_name='Calendar_Pricing', index=False)

            # --- 4. Amenities Sheet ---
            if data.get('amenities'):
                amenities_list = []
                for group in data['amenities']:
                    for amenity in group.get('values', []):
                        amenities_list.append({
                            "Group": group.get('title'), "Amenity": amenity.get('title'),
                            "Is Available": amenity.get('available')
                        })
                pd.DataFrame(amenities_list).to_excel(writer, sheet_name='Amenities', index=False)

            # --- 5. Photos Sheet ---
            if data.get('images'):
                pd.DataFrame(data['images']).to_excel(writer, sheet_name='Photos', index=False)
        
        print(f"  ✅ Excel report saved successfully.")
    except Exception as e:
        print(f"  ❌ Error creating Excel file for {url}: {e}")

def process_url(url: str, index: int):
    """
    Main function to orchestrate the scraping and saving process for a single URL.
    """
    print(f"\n▶️ Processing URL #{index}: {url}")

    match = re.search(r'/rooms/(\d+)', url)
    if not match:
        print(f"  ❌ Error: Could not find a valid listing ID in the URL. Skipping.")
        return

    listing_id = match.group(1)
    
    try:
        # 1. Scrape the data
        listing_details = pyairbnb.get_details(room_url=url) #
        print(f"  ✅ Successfully scraped listing details for ID: {listing_id}.")
        
        # 2. Define the output filenames based on the new convention
        excel_filename = f"{index}) {listing_id}.xlsx"
        
        # 3. Save the data to the Excel file
        save_as_excel(listing_details, excel_filename, url)

    except Exception as e:
        print(f"  ❌ An unexpected error occurred while processing {url}: {e}")
        print("  This could be due to an invalid URL, a network issue, or a change in the Airbnb website.")

def main():
    """
    Parses command-line arguments and initiates the bulk scraping process.
    """
    # ... (the argument parsing code stays the same) ...
    parser = argparse.ArgumentParser(
        description="Scrape details from a list of Airbnb listing URLs in a text file and save each as a separate Excel file."
    )
    parser.add_argument(
        "--file",
        type=str,
        required=True,
        help="The path to a text file containing Airbnb listing URLs, one per line."
    )
    args = parser.parse_args()
    
    try:
        with open(args.file, 'r') as f:
            urls = [line.strip() for line in f if line.strip()]
        
        if not urls:
            print("The specified file is empty or contains no valid URLs.")
            return
            
        print(f"Found {len(urls)} URLs to process.")
        
        # This is the loop we are modifying
        for i, url in enumerate(urls, 1):
            # First, process the URL as before
            process_url(url, i)
            
            # THEN, ADD THE DELAY LOGIC HERE
            # This ensures the delay happens *after* each URL is processed
            # and only if there are more URLs to go.
            if i < len(urls): # Don't wait after the very last URL
                sleep_time = random.uniform(3, 8) # Random delay between 5 and 15 seconds
                print(f"--- Pausing for {sleep_time:.2f} seconds before next scrape ---")
                time.sleep(sleep_time)
        
        print("\n🎉 All done! Bulk processing complete.")

    except FileNotFoundError:
        print(f"❌ Error: The file '{args.file}' was not found.")
    except Exception as e:
        print(f"❌ An unexpected error occurred: {e}")

if __name__ == "__main__":
    main()

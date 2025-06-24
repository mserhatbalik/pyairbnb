# USAGE: python scrape_single_listing.py --url https://www.airbnb.com/rooms/room_id

import pyairbnb
import json
import argparse
import re
import pandas as pd
from typing import Dict, Any

def save_as_excel(data: Dict[str, Any], filename: str, url: str):
    """
    Processes the detailed listing data and saves it as a multi-sheet Excel file.

    Args:
        data (Dict[str, Any]): The scraped data from pyairbnb.
        filename (str): The path for the output Excel file.
        url (str): The original URL for inclusion in the summary.
    """
    print(f"Creating Excel report at '{filename}'...")
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
                    'createdAt': 'Date',
                    'comments': 'Comment',
                    'localizedDate': 'Localized Date',
                    'reviewer.firstName': 'Reviewer Name',
                    'response': 'Host Response'
                }
                reviews_df = reviews_df[[col for col in review_cols.keys() if col in reviews_df.columns]].rename(columns=review_cols)
                reviews_df.to_excel(writer, sheet_name='Reviews', index=False)

            # --- 3. Calendar & Pricing Sheet ---
            if data.get('calendar'):
                calendar_list = []
                for month_data in data['calendar']:
                    for day_data in month_data.get('days', []):
                        calendar_list.append({
                            'Date': day_data.get('date'),
                            'Available': day_data.get('available'),
                            'Price': day_data.get('price', {}).get('nativePrice'),
                            'Min Nights': day_data.get('minNights'),
                            'Max Nights': day_data.get('maxNights'),
                        })
                pd.DataFrame(calendar_list).to_excel(writer, sheet_name='Calendar_Pricing', index=False)

            # --- 4. Amenities Sheet ---
            if data.get('amenities'):
                amenities_list = []
                for group in data['amenities']:
                    for amenity in group.get('values', []):
                        amenities_list.append({
                            "Group": group.get('title'),
                            "Amenity": amenity.get('title'),
                            "Is Available": amenity.get('available')
                        })
                pd.DataFrame(amenities_list).to_excel(writer, sheet_name='Amenities', index=False)

            # --- 5. Photos Sheet ---
            if data.get('images'):
                pd.DataFrame(data['images']).to_excel(writer, sheet_name='Photos', index=False)
        
        print("✅ Excel report saved successfully.")
    except Exception as e:
        print(f"❌ Error creating Excel file: {e}")


def save_as_json(data: Dict[str, Any], filename: str):
    """
    Saves the dictionary as a prettified JSON file.
    """
    print(f"Saving raw data to '{filename}'...")
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        print("✅ JSON file saved successfully.")
    except Exception as e:
        print(f"❌ Error saving JSON file: {e}")

def scrape_and_save(url: str):
    """
    Main function to orchestrate the scraping and saving process.
    """
    print(f"▶️ Starting scrape for listing: {url}")

    match = re.search(r'/rooms/(\d+)', url)
    if not match:
        print("❌ Error: Could not find a valid listing ID in the URL.")
        print("Please use a standard Airbnb listing URL, e.g., 'https://www.airbnb.com/rooms/123456'")
        return

    listing_id = match.group(1)
    
    try:
        listing_details = pyairbnb.get_details(room_url=url)
        print("✅ Successfully scraped listing details.")
        
        json_filename = f"listing_{listing_id}_details.json"
        excel_filename = f"listing_{listing_id}_details.xlsx"
        
        save_as_json(listing_details, json_filename)
        save_as_excel(listing_details, excel_filename, url)
        
        print(f"\n🎉 All done! Your files are ready:\n- {json_filename}\n- {excel_filename}")

    except Exception as e:
        print(f"\n❌ An unexpected error occurred during the scraping process: {e}")
        print("This could be due to an invalid URL, a network issue, or a change in the Airbnb website.")


def main():
    """
    Parses command-line arguments and initiates the script.
    """
    parser = argparse.ArgumentParser(
        description="Scrape all details from a single Airbnb listing URL and save as JSON and Excel."
    )
    parser.add_argument(
        "--url",
        type=str,
        required=True,
        help="The full URL of the Airbnb listing to scrape."
    )
    args = parser.parse_args()
    
    scrape_and_save(args.url)

if __name__ == "__main__":
    main()
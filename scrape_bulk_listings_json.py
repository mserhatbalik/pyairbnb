# USAGE: python3 scrape_bulk_listings_json.py --file listings.txt

import pyairbnb
import json
import argparse
import re
import time
import random
from typing import Dict, Any

def process_url_to_json(url: str, index: int):
    """
    Scrapes all details for a given Airbnb URL and saves the raw,
    structured data to a dedicated JSON file.

    Args:
        url (str): The Airbnb listing URL to process.
        index (int): The numerical index of the URL from the input file,
                     used for naming the output file.
    """
    print(f"\n▶️ Processing URL #{index}: {url}")

    # Use regex to reliably extract the listing ID from the URL.
    # This is more robust than splitting the URL string.
    match = re.search(r'/rooms/(\d+)', url)
    if not match:
        print(f"  ❌ Error: Could not find a valid listing ID in the URL. Skipping.")
        return

    listing_id = match.group(1)
    
    try:
        # --- 1. Scrape the Full Listing Data ---
        # This function from the pyairbnb library is the core of the scraper.
        # It retrieves all details: reviews, calendar, host info, amenities, etc.
        print(f"  Scraping details for listing ID: {listing_id}...")
        listing_details = pyairbnb.get_details(room_url=url)
        print(f"  ✅ Successfully scraped listing details.")

        # --- 2. Define the Output Filename ---
        # The filename clearly identifies the listing.
        json_filename = f"{index}) {listing_id}.json"

        # --- 3. Save the Data to a JSON File ---
        # This is the optimal format for AI analysis, as it preserves
        # the complete data structure, relationships, and metadata.
        print(f"  Saving data to '{json_filename}'...")
        with open(json_filename, 'w', encoding='utf-8') as f:
            # json.dump() writes the Python dictionary to a file in JSON format.
            # `ensure_ascii=False` correctly handles international characters.
            # `indent=4` makes the file readable if a human ever needs to look.
            json.dump(listing_details, f, ensure_ascii=False, indent=4)
        
        print(f"  ✅ JSON file saved successfully.")

    except Exception as e:
        print(f"  ❌ An unexpected error occurred while processing {url}: {e}")
        print("     This could be due to an invalid URL, a network issue, or a change in the Airbnb website.")

def main():
    """
    Main function to parse command-line arguments and orchestrate the bulk scraping process.
    """
    # Set up the argument parser to accept a file path from the command line.
    parser = argparse.ArgumentParser(
        description="Scrape full details from a list of Airbnb URLs and save each as a structured JSON file for analysis."
    )
    parser.add_argument(
        "--file",
        type=str,
        required=True,
        help="The path to a text file containing Airbnb listing URLs, one per line."
    )
    args = parser.parse_args()
    
    try:
        # Read all non-empty lines from the input file into a list of URLs.
        with open(args.file, 'r', encoding='utf-8') as f:
            urls = [line.strip() for line in f if line.strip()]
        
        if not urls:
            print("The specified file is empty or contains no valid URLs.")
            return
            
        print(f"Found {len(urls)} URLs to process.")
        
        # Loop through each URL with its index.
        for i, url in enumerate(urls, 1):
            process_url_to_json(url, i)
            
            # Pause between requests to be a good web citizen and avoid rate-limiting.
            # A random delay is better than a fixed one.
            if i < len(urls): # No need to wait after the last URL.
                sleep_time = random.uniform(3, 8) # Random delay between 3 and 8 seconds.
                print(f"--- Pausing for {sleep_time:.2f} seconds before next scrape ---")
                time.sleep(sleep_time)
        
        print("\n🎉 All done! Bulk processing complete.")

    except FileNotFoundError:
        print(f"❌ Error: The file '{args.file}' was not found.")
    except Exception as e:
        print(f"❌ An unexpected error occurred: {e}")

if __name__ == "__main__":
    main()
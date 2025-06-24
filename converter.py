import json
import pandas as pd
import os

def process_listing_data(listing):
    """
    Flattens a single listing's JSON object into a flat dictionary.
    This is necessary to convert the nested JSON structure into a 2D Excel table.

    Args:
        listing (dict): A dictionary representing a single property listing.

    Returns:
        dict: A flattened dictionary containing all the key information.
    """
    # Use .get() to safely access keys that might be missing in some records.
    # This prevents the script from crashing if a field is absent.
    price_info = listing.get('price', {})
    price_unit = price_info.get('unit', {})
    rating_info = listing.get('rating', {})
    room_id = listing.get('room_id')

    # Construct the full URL for the listing. This is a crucial piece of data you asked for.
    listing_url = f"https://www.airbnb.com/rooms/{room_id}" if room_id else "N/A"

    # The breakdown can have multiple entries, we'll just summarize it for simplicity here.
    # A more advanced approach could be to create separate rows for each breakdown item.
    price_breakdown_desc = ""
    if price_info.get('break_down'):
        # We join all description entries into a single string.
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
        'price_unit_currency_symbol': price_unit.get('curency_symbol'), # Note: Typo in original JSON is 'curency_symbol'
        'price_unit_original_amount': price_unit.get('amount'),
        'price_unit_discounted_amount': price_unit.get('discount'),
        'price_breakdown_summary': price_breakdown_desc,
        'first_image_url': listing.get('images', [{}])[0].get('url') # Get the URL of the first image
    }

def json_to_excel(input_json_path, output_excel_path):
    """
    Reads a JSON file with listing data, processes it, and saves it as an Excel file.

    Args:
        input_json_path (str): The path to the input JSON file.
        output_excel_path (str): The path where the output Excel file will be saved.
    """
    print(f"Starting the conversion process...")
    
    # Check if the input file exists
    if not os.path.exists(input_json_path):
        print(f"Error: The file '{input_json_path}' was not found.")
        return

    try:
        # Load the JSON data from the file
        with open(input_json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        print(f"Successfully loaded {len(data)} listings from '{input_json_path}'.")

        # Process each listing in the JSON file using a list comprehension
        processed_data = [process_listing_data(listing) for listing in data]

        # Create a pandas DataFrame from the list of processed dictionaries
        # A DataFrame is essentially a table, which maps perfectly to an Excel sheet.
        df = pd.DataFrame(processed_data)
        print("Successfully converted data into a DataFrame.")

        # Save the DataFrame to an Excel file
        # `index=False` prevents pandas from writing row indices into the Excel file.
        df.to_excel(output_excel_path, index=False, engine='openpyxl')
        print(f"Success! Data has been exported to '{output_excel_path}'.")

    except json.JSONDecodeError:
        print(f"Error: The file '{input_json_path}' is not a valid JSON file.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


# --- Main execution block ---
if __name__ == "__main__":
    # Define the input and output file paths.
    # You should place 'search_results_all_final.json' in the same directory as this script,
    # or provide the full path to it.
    input_file = 'search_results_all_final.json'
    output_file = 'istanbul_listings_analysis.xlsx'
    
    # Run the conversion function
    json_to_excel(input_file, output_file)
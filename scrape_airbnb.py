import pyairbnb
import json
import time

# --- Configuration ---
# Original area definition
sw_long_orig = 28.97
sw_lat_orig = 41.03
ne_long_orig = 28.98
ne_lat_orig = 41.04
# Initial grid size
grid_size = 4

# --- Bounding Box Generation ---
bounding_boxes = []
# Loop to create the 4x4 grid
for i in range(grid_size):
    for j in range(grid_size):
        # Check if this is the problematic area "Area_4_2" (i=3, j=1)
        if i == 3 and j == 1:
            # Subdivide the problematic area into a 2x2 grid
            problem_sw_lat = sw_lat_orig + i * (ne_lat_orig - sw_lat_orig) / grid_size
            problem_sw_long = sw_long_orig + j * (ne_long_orig - sw_long_orig) / grid_size
            problem_ne_lat = sw_lat_orig + (i + 1) * (ne_lat_orig - sw_lat_orig) / grid_size
            problem_ne_long = sw_long_orig + (j + 1) * (ne_long_orig - sw_long_orig) / grid_size
            
            sub_grid_size = 2
            sub_lat_step = (problem_ne_lat - problem_sw_lat) / sub_grid_size
            sub_long_step = (problem_ne_long - problem_sw_long) / sub_grid_size

            for sub_i in range(sub_grid_size):
                for sub_j in range(sub_grid_size):
                    bounding_boxes.append({
                        "sw_lat": problem_sw_lat + sub_i * sub_lat_step,
                        "sw_long": problem_sw_long + sub_j * sub_long_step,
                        "ne_lat": problem_sw_lat + (sub_i + 1) * sub_lat_step,
                        "ne_long": problem_sw_long + (sub_j + 1) * sub_long_step,
                        "name": f"Area_4_2_Sub_{sub_i+1}_{sub_j+1}"
                    })
        else:
            # Add the other, non-problematic areas as before
            bounding_boxes.append({
                "sw_lat": sw_lat_orig + i * (ne_lat_orig - sw_lat_orig) / grid_size,
                "sw_long": sw_long_orig + j * (ne_long_orig - sw_long_orig) / grid_size,
                "ne_lat": sw_lat_orig + (i + 1) * (ne_lat_orig - sw_lat_orig) / grid_size,
                "ne_long": sw_long_orig + (j + 1) * (ne_long_orig - sw_long_orig) / grid_size,
                "name": f"Area_{i+1}_{j+1}"
            })

# --- Search Execution ---
check_in = ""
check_out = ""
currency = "USD"
language = "en"
all_listings = {} # Dictionary for automatic de-duplication

for i, box in enumerate(bounding_boxes):
    print(f"\n--- Searching in area {i+1}/{len(bounding_boxes)} ({box['name']}) ---")
    try:
        search_results = pyairbnb.search_all(
            check_in=check_in,
            check_out=check_out,
            ne_lat=box["ne_lat"],
            ne_long=box["ne_long"],
            sw_lat=box["sw_lat"],
            sw_long=box["sw_long"],
            zoom_value=17, # Increased zoom level for even smaller areas
            price_min=0,
            price_max=0,
            place_type="",
            amenities=[],
            currency=currency,
            language=language,
            proxy_url=""
        )
        print(f"Found {len(search_results)} listings in this area.")
        for listing in search_results:
            all_listings[listing['room_id']] = listing

        if i < len(bounding_boxes) - 1:
            time.sleep(3)

    except Exception as e:
        print(f"An error occurred while searching area {box['name']}: {e}")

# --- Final Output ---
unique_listings = list(all_listings.values())
print(f"\n>>> Found a total of {len(unique_listings)} unique listings across all {len(bounding_boxes)} areas. <<<")

listing_urls = [f"https://www.airbnb.com/rooms/{listing['room_id']}" for listing in unique_listings]

with open('airbnb_all_listings_final.txt', 'w') as f:
    for url in listing_urls:
        f.write(f"{url}\n")
print("\nSuccessfully saved all unique listing URLs to 'airbnb_all_listings_final.txt'")

with open('search_results_all_final.json', 'w', encoding='utf-8') as f:
    json.dump(unique_listings, f, ensure_ascii=False, indent=4)
print("Full data for all unique listings saved to 'search_results_all_final.json'")
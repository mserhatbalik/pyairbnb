import pyairbnb
import json
import argparse
import re
import pandas as pd
from typing import Dict, Any

# --- Google API Imports ---
try:
    import gspread
    from gspread_dataframe import set_with_dataframe
    from oauth2client.service_account import ServiceAccountCredentials
    from googleapiclient.discovery import build
    GOOGLE_APIS_AVAILABLE = True
except ImportError:
    GOOGLE_APIS_AVAILABLE = False


def save_as_google_sheet(data: Dict[str, Any], url: str, drive_folder_name: str, share_email: str):
    """
    Automates the creation and population of a Google Sheet in a specific Drive folder.
    """
    if not GOOGLE_APIS_AVAILABLE:
        print("\n⚠️ Google API libraries not found. Skipping Google Sheets export.")
        print("Install them with: pip install gspread gspread-dataframe oauth2client google-api-python-client")
        return

    sheet_name = data.get('title', 'Untitled Airbnb Listing')
    print(f"\n▶️ Starting automated Google Sheets export for '{sheet_name}'...")

    try:
        # --- Step 1: Authenticate with both Sheets and Drive APIs ---
        scopes = [
            'https://spreadsheets.google.com/feeds',
            'https://www.googleapis.com/auth/drive'
        ]
        creds = ServiceAccountCredentials.from_json_keyfile_name('service_account.json', scopes)
        gspread_client = gspread.authorize(creds)
        drive_service = build('drive', 'v3', credentials=creds)
        print("✅ Authenticated with Google successfully.")

        # --- Step 2: Find or Create the Google Drive Folder ---
        response = drive_service.files().list(
            q=f"mimeType='application/vnd.google-apps.folder' and name='{drive_folder_name}' and trashed=false",
            spaces='drive', fields='files(id, name)').execute()
        
        if not response['files']:
            print(f"Folder '{drive_folder_name}' not found. Creating it...")
            folder_metadata = {'name': drive_folder_name, 'mimeType': 'application/vnd.google-apps.folder'}
            folder = drive_service.files().create(body=folder_metadata, fields='id').execute()
            folder_id = folder.get('id')
            print(f"✅ Created folder with ID: {folder_id}")
        else:
            folder_id = response['files'][0].get('id')
            print(f"✅ Found folder '{drive_folder_name}' with ID: {folder_id}")

        # --- Step 3: Create the new Google Sheet inside the folder ---
        sheet_metadata = {
            'name': sheet_name,
            'parents': [folder_id],
            'mimeType': 'application/vnd.google-apps.spreadsheet'
        }
        spreadsheet = drive_service.files().create(body=sheet_metadata, fields='id').execute()
        spreadsheet_id = spreadsheet.get('id')
        print(f"✅ Created new Google Sheet with ID: {spreadsheet_id}")

        # --- Step 4: Share the new sheet with your personal email ---
        permission = {'type': 'user', 'role': 'writer', 'emailAddress': share_email}
        drive_service.permissions().create(fileId=spreadsheet_id, body=permission).execute()
        print(f"✅ Shared sheet with '{share_email}'.")

        # --- Step 5: Open the new sheet with gspread and populate it ---
        sheet_to_populate = gspread_client.open_by_key(spreadsheet_id)
        
        # Prepare DataFrames (same logic as before)
        # (This section creates the data tables like Summary, Reviews, etc.)
        summary_df = pd.DataFrame({
            "Field": ["Listing URL", "Title", "Room Type"],
            "Value": [url, data.get('title', 'N/A'), data.get('room_type', 'N/A')]
        })
        reviews_df = pd.DataFrame(data.get('reviews', []))

        sheets_to_write = {"Summary": summary_df, "Reviews": reviews_df}

        for title, df in sheets_to_write.items():
            if not df.empty:
                worksheet = sheet_to_populate.add_worksheet(title=title, rows=len(df.index)+1, cols=len(df.columns)+1)
                set_with_dataframe(worksheet, df)
                print(f"Populated sheet: '{title}'...")
        
        # Delete the default first sheet
        sheet_to_populate.del_worksheet(sheet_to_populate.sheet1)
        
        sheet_url = f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}"
        print(f"✅ Google Sheets export complete. View your new sheet at: {sheet_url}")

    except FileNotFoundError:
        print("❌ Error: 'service_account.json' not found. Please place it in the project directory.")
    except Exception as e:
        print(f"❌ An unexpected error occurred during the Google Sheets export: {e}")


def save_as_local_files(data: Dict[str, Any], listing_id: str, url: str):
    """Saves data locally as JSON and Excel."""
    print("\n▶️ Saving local files...")
    # JSON
    json_filename = f"listing_{listing_id}_details.json"
    with open(json_filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    print(f"✅ Saved JSON to '{json_filename}'")
    
    # Excel
    excel_filename = f"listing_{listing_id}_details.xlsx"
    with pd.ExcelWriter(excel_filename, engine='openpyxl') as writer:
        pd.DataFrame(data.get('reviews', [])).to_excel(writer, sheet_name='Reviews', index=False)
    print(f"✅ Saved Excel to '{excel_filename}'")


def main():
    parser = argparse.ArgumentParser(description="Fully automated Airbnb listing scraper.")
    parser.add_argument("--url", type=str, required=True, help="The full URL of the Airbnb listing.")
    parser.add_argument("--drive-folder-name", type=str, help="Name of the Google Drive folder to save the sheet in.")
    parser.add_argument("--share-email", type=str, help="Your personal Google email to share the new sheet with.")
    args = parser.parse_args()

    # --- Scrape Data ---
    print(f"▶️ Starting scrape for listing: {args.url}")
    match = re.search(r'/rooms/(\d+)', args.url)
    if not match:
        print("❌ Error: Could not find a valid listing ID in the URL.")
        return
    listing_id = match.group(1)

    try:
        listing_details = pyairbnb.get_details(room_url=args.url)
        print("✅ Successfully scraped listing details.")

        # --- Save Local Files (JSON & Excel) ---
        save_as_local_files(listing_details, listing_id, args.url)

        # --- Export to Google Sheets (if folder and email are provided) ---
        if args.drive_folder_name and args.share_email:
            save_as_google_sheet(listing_details, args.url, args.drive_folder_name, args.share_email)

        print("\n🎉 All done!")

    except Exception as e:
        print(f"\n❌ An unexpected error occurred during the scraping process: {e}")


if __name__ == "__main__":
    main()
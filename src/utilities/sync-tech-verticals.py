import os
import requests
from dotenv import load_dotenv
from supabase import create_client, Client

# Load environment variables
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")  # <-- explicitly named for clarity
HUBSPOT_API_KEY = os.getenv("HUBSPOT_API_KEY")

# Initialize Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Constants
TECH_FOCUS_FIELD = "tech_focus"
HUBSPOT_FIELD_ENDPOINT = f"https://api.hubapi.com/crm/v3/properties/companies/{TECH_FOCUS_FIELD}"
HEADERS = {
    "Authorization": f"Bearer {HUBSPOT_API_KEY}",
    "Content-Type": "application/json"
}

def fetch_tech_focus_options():
    response = requests.get(HUBSPOT_FIELD_ENDPOINT, headers=HEADERS)
    response.raise_for_status()
    return response.json().get("options", [])

def truncate_table():
    print("Truncating tech_verticals table...")
    supabase.table("tech_verticals").delete().neq("name", "").execute()

def insert_new_verticals(options):
    for option in options:
        name = option.get("value")
        description = option.get("label")
        if not name or not description:
            continue
        supabase.table("tech_verticals").insert({
            "name": name,
            "description": description
        }).execute()

def main():
    print("Fetching 'Tech Focus' options from HubSpot...")
    options = fetch_tech_focus_options()
    print(f"Retrieved {len(options)} options.")
    truncate_table()
    insert_new_verticals(options)
    print("Sync complete.")

if __name__ == "__main__":
    main()
import os
import requests
from dotenv import load_dotenv

# === Load environment variables ===
load_dotenv()

HUBSPOT_TOKEN = os.getenv("HUBSPOT_TOKEN")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

HEADERS_HUBSPOT = {
    "Authorization": f"Bearer {HUBSPOT_TOKEN}",
    "Content-Type": "application/json"
}

HEADERS_SUPABASE = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json"
}

def fetch_unmapped_companies():
    response = requests.get(
        f"{SUPABASE_URL}/rest/v1/companies",
        headers=HEADERS_SUPABASE,
        params={"select": "*", "hs_synced": "is.false"}
    )
    response.raise_for_status()
    return response.json()

def transform_for_hubspot(company):
    return {
        "properties": {
            "name": company.get("name"),
            "domain": company.get("domain"),
            "website": company.get("website"),
            "industry": company.get("industry"),
            "city": company.get("city"),
            "state": company.get("state"),
            "postal_code": company.get("postal_code"),
            "linkedin_url": company.get("linkedin_url"),
            "description": company.get("description")
        }
    }

def insert_company_to_hubspot(company_payload):
    url = "https://api.hubapi.com/crm/v3/objects/companies"
    response = requests.post(url, headers=HEADERS_HUBSPOT, json=company_payload)
    if response.status_code >= 400:
        print("❌ HubSpot Error:", response.status_code)
        print("❌ Message:", response.text)
        return False
    else:
        print("✅ HubSpot Success:", response.status_code)
        return True

def mark_company_synced(supabase_id):
    response = requests.patch(
        f"{SUPABASE_URL}/rest/v1/companies?id=eq.{supabase_id}",
        headers=HEADERS_SUPABASE,
        json={"hs_synced": True}
    )
    response.raise_for_status()

if __name__ == "__main__":
    companies = fetch_unmapped_companies()
    for company in companies:
        payload = transform_for_hubspot(company)
        success = insert_company_to_hubspot(payload)
        if success:
            mark_company_synced(company["id"])
import os
import requests
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_API_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

HEADERS = {
    "apikey": SUPABASE_API_KEY,
    "Authorization": f"Bearer {SUPABASE_API_KEY}",
    "Content-Type": "application/json",
}

def insert_tech_score(company_name, raw_input, tech_area, score, rationale):
    url = f"{SUPABASE_URL}/rest/v1/tech_scores"
    payload = {
        "company_name": company_name,
        "raw_input": raw_input,
        "tech_area": tech_area,
        "score": score,
        "rationale": rationale
    }

    response = requests.post(url, headers=HEADERS, json=payload)
    if response.status_code != 201:
        print(f"❌ Error saving to Supabase: {response.status_code} - {response.text}")
    else:
        print(f"✅ Saved: {tech_area} ({score})")
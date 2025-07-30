import os
import argparse
import requests
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables from .env file
load_dotenv()

# Retrieve keys from environment
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_API_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

# Initialize OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY)

# Set headers for Supabase REST API
HEADERS = {
    "apikey": SUPABASE_API_KEY,
    "Authorization": f"Bearer {SUPABASE_API_KEY}",
    "Content-Type": "application/json"
}

def lookup_supabase(raw_value):
    """Check if a mapping already exists in Supabase"""
    url = f"{SUPABASE_URL}/rest/v1/ai_mappings?raw_value=eq.{raw_value}&field_name=eq.industry"
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        data = response.json()
        if data:
            return data[0]["mapped_value"]
    return None

def save_to_supabase(raw_value, mapped_value):
    """Save a new mapping to Supabase"""
    url = f"{SUPABASE_URL}/rest/v1/ai_mappings"
    payload = {
        "raw_value": raw_value,
        "mapped_value": mapped_value,
        "field_name": "industry"
    }
    response = requests.post(url, headers=HEADERS, json=payload)
    if response.status_code != 201:
        print(f"❌ Supabase Error {response.status_code}: {response.text}")
    return response.status_code == 201

def map_industry(raw_value):
    """Use OpenAI to map a raw industry string to a validated value"""
    system_prompt = (
        "You are an AI assistant helping align company industry values to HubSpot's validated picklist. "
        "Return only the best matching HubSpot industry value for the provided input. "
        "If the input is invalid or ambiguous, return 'Other'."
    )
    user_prompt = f"Industry: {raw_value}"

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0
    )

    return response.choices[0].message.content.strip()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Map a raw industry value to HubSpot using AI and cache it in Supabase.")
    parser.add_argument("--industry", required=True, help="Raw industry input (e.g., 'AI for cancer research')")
    args = parser.parse_args()
    raw_input = args.industry

    # Step 1: Check cache
    cached = lookup_supabase(raw_input)
    if cached:
        print(f"✅ Cached Industry: {cached}")
    else:
        # Step 2: Get AI-generated mapping
        result = map_industry(raw_input)
        print(f"🧠 AI Result: {result}", end=" ")

        # Step 3: Save new mapping to Supabase
        if save_to_supabase(raw_input, result):
            print("| Saved to Supabase ✅")
        else:
            print("| ❌ Failed to save")
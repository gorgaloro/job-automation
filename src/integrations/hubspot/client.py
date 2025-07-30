import os
import requests

HUBSPOT_API_KEY = os.getenv("HUBSPOT_API_KEY")
BASE_URL = "https://api.hubapi.com"

HEADERS = {
    "Authorization": f"Bearer {HUBSPOT_API_KEY}",
    "Content-Type": "application/json"
}

def create_company(data):
    url = f"{BASE_URL}/crm/v3/objects/companies"
    response = requests.post(url, headers=HEADERS, json={"properties": data})
    response.raise_for_status()
    return response.json()

def create_deal(data):
    url = f"{BASE_URL}/crm/v3/objects/deals"
    response = requests.post(url, headers=HEADERS, json={"properties": data})
    response.raise_for_status()
    return response.json()

def create_contact(data):
    url = f"{BASE_URL}/crm/v3/objects/contacts"
    response = requests.post(url, headers=HEADERS, json={"properties": data})
    response.raise_for_status()
    return response.json()

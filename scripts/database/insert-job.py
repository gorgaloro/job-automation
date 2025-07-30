import os
import requests
import datetime
from dotenv import load_dotenv

# === Load environment variables ===
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json"
}

# === Insert or retrieve company ===
def insert_company(data):
    response = requests.get(
        f"{SUPABASE_URL}/rest/v1/companies",
        headers=HEADERS,
        params={"domain": f"eq.{data['domain']}", "select": "id"}
    )
    response.raise_for_status()
    results = response.json()

    if results:
        return results[0]["id"]
    else:
        post = requests.post(
            f"{SUPABASE_URL}/rest/v1/companies",
            headers=HEADERS,
            json=data
        )
        post.raise_for_status()
        confirm = requests.get(
            f"{SUPABASE_URL}/rest/v1/companies",
            headers=HEADERS,
            params={"select": "id", "order": "id.desc", "limit": 1}
        )
        confirm.raise_for_status()
        return confirm.json()[0]["id"]

# === Insert job ===
def insert_job(data):
    response = requests.post(
        f"{SUPABASE_URL}/rest/v1/jobs",
        headers=HEADERS,
        json=data
    )
    response.raise_for_status()
    return response.status_code

# === Example: Cedars-Sinai ===
company_data = {
    "name": "Cedars-Sinai Medical Center",
    "website": "https://www.cedars-sinai.org",
    "domain": "cedars-sinai.org",
    "industry": "Healthcare",
    "city": "Los Angeles",
    "state": "CA",
    "postal_code": "90048",
    "employees": 14000,
    "annual_revenue": None,
    "linkedin_url": "https://www.linkedin.com/company/cedars-sinai"
}

job_data = {
    "job_title": "IT Project Manager",
    "job_board_url": "https://careers.cedars-sinai.edu/jobs/IT-Project-Manager",
    "company_job_board_url": "https://careers.cedars-sinai.edu/",
    "salary_min": None,
    "salary_max": None,
    "job_description_url": "https://careers.cedars-sinai.edu/jobs/IT-Project-Manager",
    "research": True,
    "created_at": datetime.datetime.now().isoformat()
}

# === Run It ===
if __name__ == "__main__":
    company_id = insert_company(company_data)
    job_data["company_id"] = company_id
    result = insert_job(job_data)
    print("✅ Job inserted with status code:", result)
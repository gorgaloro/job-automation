import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

company_name = "Lovable"
company_url = "https://lovable.dev/"
tech_areas = [
    "AI/ML", "HealthTech", "FinTech", "PropTech", "CommunityTech", "RetailTech", "GreenTech",
    "EdTech", "LegalTech", "GovTech", "HRTech", "AgriTech", "MobilityTech", "SpaceTech", 
    "DeepTech", "Cybersecurity", "GamingTech", "FoodTech", "EventTech", "Customer Experience Tech",
    "SalesTech", "B2B Software", "Smart Cities", "LogisticsTech", "Wearable Tech", 
    "Quantum Computing", "Cloud Computing", "WebTech", "CollaborationTech", "Community Hosting", "Other"
]

system_prompt = (
    f"You are an AI assistant helping evaluate a company's technology involvement. "
    f"Given the company name and website, rate the company's involvement in each tech area "
    f"from 0 to 100 (where 0 = not involved, 100 = core business). "
    f"Also include a short 1-2 sentence rationale for any score ≥ 60."
)

user_prompt = f"Company: {company_name}\nWebsite: {company_url}\n\nTech Areas:\n" + "\n".join(tech_areas)

response = client.chat.completions.create(
    model="gpt-4",
    messages=[
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ],
    temperature=0.2
)

print(response.choices[0].message.content.strip())
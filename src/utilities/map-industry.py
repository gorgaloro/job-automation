import os
import argparse
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def map_industry(raw_industry):
    system_prompt = (
        "You are an AI assistant helping align company industry values to HubSpot's validated picklist."
        "Return only the best matching HubSpot industry value for the provided input."
        "If the input is invalid or ambiguous, return 'Other'."
    )
    user_prompt = f"Industry: {raw_industry}"

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
    parser = argparse.ArgumentParser(description="Map a raw industry value to a HubSpot validated industry.")
    parser.add_argument("--industry", required=True, help="Raw industry value (e.g., 'Life sciences and pharma')")
    args = parser.parse_args()

    result = map_industry(args.industry)
    print(f"✅ Mapped Industry: {result}")
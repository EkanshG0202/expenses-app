import os
import requests
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY")
TOGETHER_URL = "https://api.together.xyz/v1/chat/completions"

HEADERS = {
    "Authorization": f"Bearer {TOGETHER_API_KEY}",
    "Content-Type": "application/json"
}


def classify_transaction_with_llm(description: str) -> str:
    prompt = f"""
    Categorize the following bank transaction into one of these categories:
    [Groceries, Dining, Entertainment, Utilities, Rent, Travel, Shopping, Medical, Education, Income, Other].

    Transaction Description: "{description}"
    Category:
    """

    payload = {
        "model": "meta-llama/Llama-3.3-70B-Instruct-Turbo-Free",
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.3,
        "max_tokens": 10,
    }

    try:
        response = requests.post(TOGETHER_URL, headers=HEADERS, json=payload)
        response.raise_for_status()
        content = response.json()
        return content["choices"][0]["message"]["content"].strip()
    except Exception as e:
        print(f"LLM classification error: {e}")
        return "Other"


def generate_insights_llm(month: str, total_spent: float, budget: float, breakdown: dict) -> str:
    category_insights = "\n".join([f"- {cat}: ₹{amt:.2f}" for cat, amt in breakdown.items()])

    prompt = f"""
You are a personal finance assistant.

Summarize this user's monthly spending in a friendly and professional tone.

Month: {month}
Budget: ₹{budget}
Total Spent: ₹{total_spent}
Category-wise Spending:
{category_insights}

Give insights like:
- How they are doing overall
- Which categories are high or low
- Where they can save
- If they are within or over budget

Keep it short (3-5 sentences).
"""

    payload = {
        "model": "meta-llama/Llama-3.3-70B-Instruct-Turbo-Free",
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7,
        "max_tokens": 300,
    }

    try:
        response = requests.post(TOGETHER_URL, headers=HEADERS, json=payload)
        response.raise_for_status()
        content = response.json()
        return content["choices"][0]["message"]["content"].strip()
    except Exception as e:
        print(f"LLM insights generation error: {e}")
        return "Could not generate insights at this time."

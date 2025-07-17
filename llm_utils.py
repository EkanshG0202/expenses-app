import os
import requests

TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY")  # Ensure this is set in your environment
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
        "model": "mistralai/Mistral-7B-Instruct-v0.3",
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

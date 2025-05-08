import requests

API_KEY = "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"
URL = "https://api.groq.com/llama"  # Update this to the correct endpoint

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}
payload = {
    "prompt": "Test prompt",
    "model": "llama-3.3",
    "temperature": 0.7
}

try:
    response = requests.post(URL, headers=headers, json=payload)
    response.raise_for_status()
    print(response.json())
except requests.exceptions.RequestException as e:
    print(f"Error: {e}")
# Add this function in importrequests.py


import os
import time
from groq import Groq
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_groq_client():
    """Initialize and return Groq client with API key"""
    api_key = os.getenv('GROQ_API_KEY')
    if not api_key:
        raise ValueError("GROQ_API_KEY not found in environment variables")
    return Groq(api_key=api_key)

def infer_with_groq_api(messages, model="mistral-saba-24b", temperature=0.7, max_tokens=1024, top_p=0.9):
    """
    Interact with the Groq API using the specified model and messages.
    """
    try:
        client = get_groq_client()
        completion = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            top_p=top_p,
            stream=False
        )
        return completion.choices[0].message.content.strip()
    except Exception as e:
        raise Exception(f"API Error: {str(e)}")

def infer_with_retry(messages, max_retries=3):
    """
    Retry API calls with exponential backoff.
    """
    for attempt in range(max_retries):
        try:
            return infer_with_groq_api(messages)
        except Exception as e:
            if attempt == max_retries - 1:
                raise
            wait_time = 2 ** attempt
            print(f"Attempt {attempt + 1} failed. Retrying in {wait_time} seconds...")
            time.sleep(wait_time)
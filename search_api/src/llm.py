import os

from openai import OpenAI

VAST_IP_ADDRESS = os.getenv("VAST_IP_ADDRESS", "")
VAST_PORT = os.getenv("VAST_PORT", "80")
openai_api_key = os.getenv("OPENAI_API_KEY", default="EMPTY")
if VAST_IP_ADDRESS:
    openai_api_base = f"http://{VAST_IP_ADDRESS}:{VAST_PORT}/v1"
    model_name = "google/gemma-3-4b-it"
else:
    openai_api_base = "https://api.openai.com/v1"
    model_name = 'gpt-4o-mini'

client = OpenAI(
    api_key=openai_api_key,
    base_url=openai_api_base
)

def chat_complete(messages=(), model=model_name, raw=False):
    response = client.chat.completions.create(
        model=model,
        messages=messages
    )
    if raw:
        return response.choices[0].message
    output = response.choices[0].message
    return output.content
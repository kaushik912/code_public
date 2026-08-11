"""
OpenRouter via the native `openrouter` PyPI package (v0.10.8).

Note: this package's chat method is `client.chat.send(...)`, NOT
`client.chat.completions.create(...)`. The latter is the OpenAI-SDK style
(see main_openai.py).

Run:  python main.py
"""
import os

from dotenv import load_dotenv
from openrouter import OpenRouter

load_dotenv()

client = OpenRouter(api_key=os.environ["OPENROUTER_API_KEY"])

resp = client.chat.send(
    model="meta-llama/llama-3.3-70b-instruct",
    messages=[{"role": "user", "content": "Tell me a joke."}],
)

print("model used :", resp.model)
print("reply      :", resp.choices[0].message.content)

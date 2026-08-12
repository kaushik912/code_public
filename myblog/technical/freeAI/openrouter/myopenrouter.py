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

## use openrouter/free will auto-select the free model
## other options : meta-llama/llama-3.3-70b-instruct
## cohere/north-mini-code:free: good for coding
resp = client.chat.send(
    model="openrouter/free",
    messages=[{"role": "user", "content": "Count vowels in the following text: Welcome"}],
)

print("model used :", resp.model)
print("reply      :", resp.choices[0].message.content)

from google import genai
client = genai.Client()

## just export GEMINI_API_KEY and run the script

## Models tested:
## gemini-flash-lite-latest
## gemini-3.6-flash
response = client.models.generate_content(
    model='gemini-flash-lite-latest',
    contents='Tell me a joke in 100 words.'
)
print(response.text)

print(response.model_dump_json(
    exclude_none=True, indent=4))
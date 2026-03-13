from dotenv import load_dotenv
from google import genai
from leaftrail import leaftrail  # Assuming this is your custom decorator
import os

load_dotenv()

# Specify the api_key parameter explicitly
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

@leaftrail
def ask_gemini(model, prompt):
    # This matches the google-genai SDK structure
    return client.models.generate_content(
        model=model,
        contents=prompt
    )

# Running the tool
response = ask_gemini(
    model="gemini-2.5-flash", 
    prompt="Explain the environmental impact of data centers in 2 sentences."
)

# To see the text, you usually access .text
print(response.text)
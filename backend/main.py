from fastapi import FastAPI
# This is a minor change to trigger CI/CD for backend
from pydantic import BaseModel
import vertexai
from vertexai.generative_models import GenerativeModel
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

class Prompt(BaseModel):
    text: str

# Initialize Vertex AI
try:
    vertexai.init(project=os.getenv("GCP_PROJECT_ID"), location=os.getenv("GCP_REGION"))
    gen_model = GenerativeModel("gemini-1.0-pro")
    print("Vertex AI initialized successfully.")
except Exception as e:
    print(f"Error initializing Vertex AI: {e}")
    gen_model = None

@app.get("/api/message")
def get_message():
    return {"message": "Hello from the backend!"}

@app.post("/api/generate")
async def generate_text(prompt: Prompt):
    if not gen_model:
        return {"error": "Vertex AI not initialized"}, 500

    try:
        response = gen_model.generate_content(prompt.text)
        return {"response": response.text}
    except Exception as e:
        return {"error": str(e)}, 500

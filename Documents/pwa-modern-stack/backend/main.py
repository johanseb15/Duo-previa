from fastapi import FastAPI
from dotenv import load_dotenv
import os

# Cargar variables de entorno Desde .env
load_dotenv()

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/api/message")
def get_message():
    return {"message": "Este es un mensaje desde el backend"}

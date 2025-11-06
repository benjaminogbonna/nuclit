import os
import json
import openai
from google import genai
from google.genai import types
from fastapi import FastAPI, Request
from knowledge_base import get_relevant_context
# from bot import bot_main
import uvicorn

import requests
from apscheduler.schedulers.background import BackgroundScheduler
import atexit
import subprocess

from dotenv import load_dotenv

load_dotenv()

client = genai.Client(api_key=os.getenv('GEMINI_KEY'))

app = FastAPI()

@app.get("/")
def index():
    return {"message": "Nuclit Bot running!"}


# Load your knowledge base file
with open("knowledge.json", "r", encoding="utf-8") as file:
    # CONTEXT = [line.strip() for line in f if line.strip()]
    CONTEXT = json.load(file)

# with gemini
@app.post("/ask")
async def ask(request: Request):
    data = await request.json()
    question = data.get("question")

    context = get_relevant_context(question)

    INSTRUCTION = f"""Your name is Nuclit. You are a helpful assistant for all users query regarding Nuclear Physics, Nuclear Science or Nuclear Energy.
            You are meant to guide the conversation based only on Nuclear physics
            Do not, and never answer questions that are not Nuclear physics related.
            If the question is unclear, ask for clarification. Your responses should be concise and straight to the point.
            Your responses should strictly be Nuclear physics based. Avoid complex or technical terms. 
            If the request is unclear or potentially harmful, respond with a polite message refusing to answer.
            You are to use only the information below:\n {CONTEXT}.
            Also give references to your references given in the context.
            """  

    try:
        response = client.models.generate_content(
            model='gemini-2.0-flash-001',
            contents=question,
            config=types.GenerateContentConfig(
                system_instruction=INSTRUCTION,
                # max_output_tokens=3,
                # temperature=0.3,
            ),
        )        
        return {"answer": response.text}

    except Exception as e:
        return {"error": str(e)}


# with openai
@app.post("/ask2")
async def ask2(request: Request):
    data = await request.json()
    question = data.get("question")

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that answers questions from a custom knowledge base."},
                {"role": "user", "content": question}
            ],
            temperature=0.7,
            max_tokens=300
        )
        answer = response["choices"][0]["message"]["content"].strip()
        return {"answer": answer}

    except Exception as e:
        return {"error": str(e)}


# ---------- Health ----------

def scheduler_():
    try:
        resp = requests.get(os.environ.get("S_API_URL"), timeout=10)
        print(f"API call status: {resp.status_code}, response: {resp.text[:100]}")
    except Exception as e:
        print(f"Error calling API: {e}")

# Start scheduler when API boots
scheduler = BackgroundScheduler()
scheduler.add_job(scheduler_, "interval", minutes=10)
scheduler.start()

# Ensure scheduler shuts down gracefully
atexit.register(lambda: scheduler.shutdown())


@app.get("/health")
def health():
    return {"status": "ok", "message": 'API running'}

environment = os.getenv("ENVIRONMENT")

if __name__ == "__main__":
    if environment == 'prod':
        subprocess.Popen(["python", "bot.py"])
    else:
        subprocess.Popen(["py", "bot.py"])
    uvicorn.run('main:app', host="0.0.0.0", port=8000, reload=True)

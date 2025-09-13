from transformers import pipeline
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()
chatbot = pipeline("text-generation", model="gpt2")

class UserInput(BaseModel):
    text: str

@app.post("/chat")
def chat(user_input: UserInput):
    response = chatbot(user_input.text, max_length=100, num_return_sequences=1)
    return {"reply": response[0]["generated_text"]}

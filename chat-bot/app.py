import os
import logging
from transformers import pipeline, AutoTokenizer, AutoModelForCausalLM
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, StreamingResponse
from pydantic import BaseModel
import torch
import json
import asyncio
from typing import Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Professional Chatbot API",
    description="A lightweight chatbot powered by HuggingFace Transformers",
    version="1.0.0"
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variables for model
chatbot = None
tokenizer = None

class ChatRequest(BaseModel):
    message: str
    max_length: Optional[int] = 100
    temperature: Optional[float] = 0.7

class ChatResponse(BaseModel):
    reply: str
    status: str = "success"

def load_lightweight_model():
    """Load a lightweight model suitable for EC2 deployment"""
    global chatbot, tokenizer
    
    try:
        # Use DistilGPT-2 for better performance
        model_name = "distilgpt2"
        logger.info(f"Loading model: {model_name}")
        
        # Load tokenizer and model separately for better control
        tokenizer = AutoTokenizer.from_pretrained(
            model_name,
            cache_dir="./model_cache"
        )
        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token
            
        # Use CPU for lightweight deployment with memory optimization
        device = "cpu"
        chatbot = pipeline(
            "text-generation",
            model=model_name,
            tokenizer=tokenizer,
            device=device,
            framework="pt",
            clean_up_tokenization_spaces=True,
            cache_dir="./model_cache",
            # Memory optimization settings
            torch_dtype="auto",
            low_cpu_mem_usage=True
        )
        
        logger.info("Model loaded successfully")
        return True
        
    except Exception as e:
        logger.error(f"Error loading model: {str(e)}")
        return False

@app.on_event("startup")
async def startup_event():
    """Initialize the model on startup"""
    success = load_lightweight_model()
    if not success:
        logger.error("Failed to load model on startup")

@app.get("/", response_class=HTMLResponse)
async def read_root():
    """Serve the main chat interface"""
    try:
        with open("static/index.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        return HTMLResponse(
            content="<h1>Chatbot API</h1><p>Frontend not found. API is running at /docs</p>"
        )

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    model_status = "loaded" if chatbot is not None else "not_loaded"
    return {
        "status": "healthy",
        "model_status": model_status,
        "message": "Chatbot API is running"
    }

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Main chat endpoint with error handling"""
    if chatbot is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    try:
        # Validate input
        if not request.message.strip():
            raise HTTPException(status_code=400, detail="Message cannot be empty")
        
        # Limit message length for performance
        if len(request.message) > 500:
            raise HTTPException(status_code=400, detail="Message too long (max 500 characters)")
        
        # Generate response
        prompt = f"Human: {request.message}\nAssistant:"
        
        response = chatbot(
            prompt,
            max_length=min(request.max_length, 150),
            num_return_sequences=1,
            temperature=request.temperature,
            do_sample=True,
            pad_token_id=tokenizer.eos_token_id,
            truncation=True
        )
        
        # Clean up the response
        generated_text = response[0]["generated_text"]
        reply = generated_text.replace(prompt, "").strip()
        
        # Remove any remaining "Human:" or "Assistant:" prefixes
        reply = reply.replace("Human:", "").replace("Assistant:", "").strip()
        
        if not reply:
            reply = "I'm sorry, I couldn't generate a response. Could you try rephrasing your question?"
        
        return ChatResponse(reply=reply)
        
    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/chat/stream")
async def chat_stream(message: str):
    """Streaming chat endpoint for real-time responses"""
    if chatbot is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    async def generate_stream():
        try:
            prompt = f"Human: {message}\nAssistant:"
            
            # For streaming, we'll simulate token-by-token generation
            response = chatbot(
                prompt,
                max_length=100,
                num_return_sequences=1,
                temperature=0.7,
                do_sample=True,
                pad_token_id=tokenizer.eos_token_id
            )
            
            reply = response[0]["generated_text"].replace(prompt, "").strip()
            
            # Simulate streaming by yielding chunks
            words = reply.split()
            for i, word in enumerate(words):
                chunk = {"token": word + " ", "done": False}
                yield f"data: {json.dumps(chunk)}\n\n"
                await asyncio.sleep(0.1)  # Simulate processing time
            
            # Final chunk
            yield f"data: {json.dumps({'token': '', 'done': True})}\n\n"
            
        except Exception as e:
            error_chunk = {"error": str(e), "done": True}
            yield f"data: {json.dumps(error_chunk)}\n\n"
    
    return StreamingResponse(
        generate_stream(),
        media_type="text/plain",
        headers={"Cache-Control": "no-cache", "Connection": "keep-alive"}
    )

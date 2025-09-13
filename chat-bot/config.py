# Chatbot Configuration for EC2 Deployment

import os
from typing import Optional

class Config:
    # Model Configuration
    MODEL_NAME = os.getenv("MODEL_NAME", "distilgpt2")  # Lightweight model for EC2
    MAX_MODEL_LENGTH = int(os.getenv("MAX_MODEL_LENGTH", "150"))
    MODEL_CACHE_DIR = os.getenv("MODEL_CACHE_DIR", "./model_cache")
    
    # Performance Settings
    USE_CPU_ONLY = os.getenv("USE_CPU_ONLY", "true").lower() == "true"
    MAX_WORKERS = int(os.getenv("MAX_WORKERS", "1"))  # Single worker for small EC2
    MEMORY_LIMIT_GB = float(os.getenv("MEMORY_LIMIT_GB", "1.0"))
    
    # API Settings
    MAX_MESSAGE_LENGTH = int(os.getenv("MAX_MESSAGE_LENGTH", "500"))
    REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "30"))
    RATE_LIMIT_PER_MINUTE = int(os.getenv("RATE_LIMIT_PER_MINUTE", "60"))
    
    # Server Settings
    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", "8000"))
    DEBUG = os.getenv("DEBUG", "false").lower() == "true"
    
    # Security
    ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "*").split(",")
    
    # Logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE = os.getenv("LOG_FILE", "chatbot.log")
    
    @classmethod
    def get_model_config(cls):
        """Get optimized model configuration for EC2"""
        return {
            "model_name": cls.MODEL_NAME,
            "cache_dir": cls.MODEL_CACHE_DIR,
            "device": "cpu" if cls.USE_CPU_ONLY else "auto",
            "torch_dtype": "float32",  # Use float32 for CPU
            "low_cpu_mem_usage": True,
            "trust_remote_code": False
        }
    
    @classmethod
    def get_generation_config(cls):
        """Get optimized generation configuration"""
        return {
            "max_length": cls.MAX_MODEL_LENGTH,
            "temperature": 0.7,
            "do_sample": True,
            "top_p": 0.9,
            "top_k": 50,
            "repetition_penalty": 1.1,
            "pad_token_id": None,  # Will be set by tokenizer
            "eos_token_id": None,  # Will be set by tokenizer
        }
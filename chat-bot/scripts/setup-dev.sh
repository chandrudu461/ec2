#!/bin/bash

# Development setup script
# Run this locally for development

echo "🔧 Setting up development environment..."

# Create virtual environment
python -m venv venv

# Activate virtual environment
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" ]]; then
    source venv/Scripts/activate
else
    source venv/bin/activate
fi

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Create necessary directories
mkdir -p logs
mkdir -p model_cache

# Set environment variables for development
export MODEL_NAME=distilgpt2
export USE_CPU_ONLY=true
export DEBUG=true
export LOG_LEVEL=DEBUG

echo "✅ Development environment ready!"
echo ""
echo "🚀 To start the development server:"
echo "   uvicorn app:app --reload --host 0.0.0.0 --port 8000"
echo ""
echo "🌐 Access the application at:"
echo "   http://localhost:8000"
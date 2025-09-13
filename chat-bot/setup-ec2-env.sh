#!/bin/bash

# EC2 Environment Setup Script
# Run this on your EC2 instance after cloning the repository

echo "🚀 Setting up Professional Chatbot on EC2..."

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p logs
mkdir -p model_cache
mkdir -p nginx/ssl

# Set proper permissions
chmod 755 logs
chmod 755 model_cache
chmod 755 scripts/*.sh

# Create environment file for Docker Compose
echo "⚙️ Creating environment configuration..."
cat << EOF > .env
# Model Configuration
MODEL_NAME=distilgpt2
USE_CPU_ONLY=true
MAX_WORKERS=1
MEMORY_LIMIT_GB=1.0

# Server Configuration  
HOST=0.0.0.0
PORT=8000
LOG_LEVEL=INFO

# Security
DEBUG=false

# Paths
MODEL_CACHE_DIR=/app/model_cache
LOG_FILE=/app/logs/chatbot.log
EOF

# Install additional system dependencies if needed
echo "📦 Installing system dependencies..."
if command -v yum &> /dev/null; then
    # Amazon Linux / CentOS / RHEL
    sudo yum install -y curl wget htop
elif command -v apt &> /dev/null; then
    # Ubuntu / Debian
    sudo apt update
    sudo apt install -y curl wget htop
fi

# Create a simple monitoring script
echo "📊 Creating monitoring script..."
cat << 'EOF' > monitor.sh
#!/bin/bash
echo "=== Chatbot System Status ==="
echo "Date: $(date)"
echo ""

echo "🐳 Docker Status:"
sudo systemctl status docker --no-pager -l

echo ""
echo "📦 Container Status:"
docker-compose ps

echo ""
echo "💾 System Resources:"
free -h
df -h /

echo ""
echo "🌐 Application Health:"
curl -s http://localhost/health | jq . 2>/dev/null || curl -s http://localhost/health

echo ""
echo "📊 Container Stats:"
docker stats --no-stream
EOF

chmod +x monitor.sh

echo "✅ Environment setup completed!"
echo ""
echo "🎯 Next steps:"
echo "1. Build and start the application:"
echo "   docker-compose up --build -d"
echo ""
echo "2. Check status:"
echo "   docker-compose ps"
echo ""
echo "3. View logs:"
echo "   docker-compose logs -f"
echo ""
echo "4. Monitor system:"
echo "   ./monitor.sh"
echo ""
echo "5. Access your chatbot at:"
echo "   http://$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4 2>/dev/null || echo 'YOUR-EC2-PUBLIC-IP')"
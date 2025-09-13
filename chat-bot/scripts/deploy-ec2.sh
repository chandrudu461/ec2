#!/bin/bash

# EC2 Deployment Script for Professional Chatbot
# Run this script on your EC2 instance

set -e

echo "🚀 Starting Professional Chatbot deployment on EC2..."

# Update system
echo "📦 Updating system packages..."
sudo yum update -y

# Install Docker
echo "🐳 Installing Docker..."
sudo yum install -y docker
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -aG docker ec2-user

# Install Docker Compose
echo "🔧 Installing Docker Compose..."
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Create application directory
echo "📁 Setting up application directory..."
sudo mkdir -p /opt/chatbot
sudo chown ec2-user:ec2-user /opt/chatbot
cd /opt/chatbot

# Clone or copy application files (assuming files are already present)
echo "📋 Application files should be in /opt/chatbot"

# Set up environment variables
echo "⚙️ Setting up environment variables..."
cat << EOF > .env
MODEL_NAME=distilgpt2
USE_CPU_ONLY=true
MAX_WORKERS=1
MEMORY_LIMIT_GB=1.0
LOG_LEVEL=INFO
HOST=0.0.0.0
PORT=8000
EOF

# Create systemd service
echo "🔄 Creating systemd service..."
sudo tee /etc/systemd/system/chatbot.service > /dev/null << EOF
[Unit]
Description=Professional Chatbot Service
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/opt/chatbot
ExecStart=/usr/local/bin/docker-compose up -d
ExecStop=/usr/local/bin/docker-compose down
TimeoutStartSec=0
User=ec2-user
Group=ec2-user

[Install]
WantedBy=multi-user.target
EOF

# Enable and start service
echo "🎯 Enabling and starting chatbot service..."
sudo systemctl daemon-reload
sudo systemctl enable chatbot.service

# Build and start the application
echo "🏗️ Building and starting the application..."
newgrp docker << END
docker-compose build
docker-compose up -d
END

# Set up log rotation
echo "📝 Setting up log rotation..."
sudo tee /etc/logrotate.d/chatbot > /dev/null << EOF
/opt/chatbot/logs/*.log {
    daily
    missingok
    rotate 7
    compress
    delaycompress
    notifempty
    create 644 ec2-user ec2-user
    postrotate
        docker-compose restart > /dev/null 2>&1 || true
    endscript
}
EOF

# Set up basic firewall rules
echo "🔒 Setting up firewall rules..."
sudo yum install -y firewalld
sudo systemctl start firewalld
sudo systemctl enable firewalld
sudo firewall-cmd --permanent --add-port=80/tcp
sudo firewall-cmd --permanent --add-port=443/tcp
sudo firewall-cmd --reload

# Create health check script
echo "💊 Creating health check script..."
cat << 'EOF' > /opt/chatbot/health_check.sh
#!/bin/bash
response=$(curl -s -o /dev/null -w "%{http_code}" http://localhost/health)
if [ $response -eq 200 ]; then
    echo "$(date): Health check passed"
    exit 0
else
    echo "$(date): Health check failed with code $response"
    exit 1
fi
EOF
chmod +x /opt/chatbot/health_check.sh

# Set up cron job for health monitoring
echo "⏰ Setting up health monitoring..."
(crontab -l 2>/dev/null; echo "*/5 * * * * /opt/chatbot/health_check.sh >> /opt/chatbot/logs/health.log 2>&1") | crontab -

echo "✅ Deployment completed successfully!"
echo ""
echo "🌐 Your chatbot is now running and accessible at:"
echo "   http://$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4)"
echo ""
echo "📊 To monitor the application:"
echo "   sudo systemctl status chatbot"
echo "   docker-compose logs -f"
echo ""
echo "🔧 To manage the application:"
echo "   sudo systemctl start chatbot    # Start"
echo "   sudo systemctl stop chatbot     # Stop"
echo "   sudo systemctl restart chatbot  # Restart"
echo ""
echo "📝 Logs are available at:"
echo "   /opt/chatbot/logs/"
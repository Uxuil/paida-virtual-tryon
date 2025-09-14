#!/bin/bash

# PAIDA Virtual Try-On Setup Script
echo "🚀 Setting up PAIDA Virtual Try-On project..."

# Check if .env file exists
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp env.example .env
    echo "⚠️  Please edit .env file with your actual API keys and credentials"
    echo "   Required: DASHSCOPE_API_KEY, OSS credentials, JWT_SECRET_KEY"
else
    echo "✅ .env file already exists"
fi

# Create upload directories
echo "📁 Creating upload directories..."
mkdir -p backend/uploads
mkdir -p uploads

# Install Python dependencies
echo "🐍 Installing Python dependencies..."
cd backend
pip install -r requirements.txt
cd ..

echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env file with your actual credentials"
echo "2. Start backend: cd backend && python app.py"
echo "3. Start frontend: cd frontend && python -m http.server 8080"
echo "4. Visit http://localhost:8080"
echo ""
echo "🔐 Security reminder: Never commit .env files to Git!"
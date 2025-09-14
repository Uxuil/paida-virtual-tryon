# PAIDA Virtual Try-On

AI-powered virtual try-on application that allows users to upload photos and see how different garments look on them.

## 🚀 Features

- **AI-Powered Virtual Try-On**: Upload person and garment photos to see realistic try-on results
- **Multiple Garment Types**: Support for tops, bottoms, and dresses
- **Modern UI**: Beautiful, responsive interface with drag-and-drop functionality
- **Real-time Processing**: Live progress tracking and notifications
- **Mobile Friendly**: Optimized for both desktop and mobile devices

## 🛠️ Tech Stack

### Frontend
- HTML5, CSS3, JavaScript (ES6+)
- Font Awesome icons
- Responsive design with CSS Grid and Flexbox
- Drag and drop file upload

### Backend
- Python Flask
- Alibaba Cloud DashScope API
- Alibaba Cloud OSS for file storage
- JWT authentication

## 📦 Installation

### Prerequisites
- Python 3.8+
- Node.js (for frontend development)
- Alibaba Cloud account with DashScope and OSS access

### 1. Clone the repository
```bash
git clone https://github.com/your-username/paida-virtual-tryon.git
cd paida-virtual-tryon
```

### 2. Configure environment variables
```bash
# Copy the environment template
cp env.example .env

# Edit .env with your actual credentials
nano .env
```

Required environment variables:
```bash
DASHSCOPE_API_KEY=your_dashscope_api_key
OSS_ACCESS_KEY_ID=your_oss_access_key_id
OSS_ACCESS_KEY_SECRET=your_oss_access_key_secret
OSS_ENDPOINT=your_oss_endpoint
OSS_BUCKET_NAME=your_bucket_name
JWT_SECRET_KEY=your_jwt_secret_key
```

### 3. Install backend dependencies
```bash
cd backend
pip install -r requirements.txt
```

### 4. Run the application
```bash
# Terminal 1: Start backend
cd backend
python app.py

# Terminal 2: Start frontend
cd frontend
python -m http.server 8080
```

Visit `http://localhost:8080` to use the application.

## 🔐 Security

**Important**: This project uses environment variables for sensitive information. Never commit `.env` files to version control.

See [SECURITY.md](SECURITY.md) for detailed security configuration instructions.

## 📁 Project Structure

```
paida-virtual-tryon/
├── backend/
│   ├── app.py              # Main Flask application
│   ├── config.py           # Configuration settings
│   ├── requirements.txt    # Python dependencies
│   └── utils/
│       └── aliyun_client.py # Alibaba Cloud client
├── frontend/
│   ├── index.html          # Main HTML file
│   ├── style.css           # Stylesheet
│   ├── script.js           # JavaScript functionality
│   └── test.html           # Upload test page
├── test-images/            # Sample images for testing
├── docker-compose.yml      # Docker configuration
├── dockerfile             # Docker image definition
├── env.example            # Environment variables template
├── .gitignore            # Git ignore rules
└── SECURITY.md           # Security configuration guide
```

## 🐳 Docker Deployment

```bash
# Build and run with Docker Compose
docker-compose up --build
```

## 📱 Usage

1. **Upload Person Photo**: Click or drag a full-body photo of a person
2. **Upload Garment Photo**: Click or drag a photo of the garment you want to try on
3. **Select Garment Type**: Choose between Top, Bottom, or Dress
4. **Start AI Try-On**: Click the "Start AI Try-On" button
5. **View Results**: Wait for processing and view the virtual try-on result
6. **Download**: Save the result image to your device

## 🔧 API Endpoints

- `POST /api/tryon/upload` - Upload image files
- `POST /api/tryon/direct` - Start virtual try-on process
- `GET /api/tryon/status/{task_id}` - Check task status
- `GET /api/health` - Health check

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

If you encounter any issues or have questions, please:

1. Check the [SECURITY.md](SECURITY.md) for configuration issues
2. Open an issue on GitHub
3. Contact the development team

## 🙏 Acknowledgments

- Alibaba Cloud for providing the AI and storage services
- The open-source community for various libraries and tools

# 🧠 Resume Parser App

An AI-powered web app that extracts key details from uploaded resumes (PDF) and lets users ask questions about the candidate using Google Gemini.

## 🚀 Features
- Upload PDF resume and extract fields (Name, Email, Skills, etc.)
- Preview resume file in-browser
- Ask custom questions using Gemini API
- Optional LinkedIn data integration

## 🛠 Setup

1. Clone the repo:
   ```bash
   git clone https://github.com/your-username/resume-parser-app.git
   cd resume-parser-app
2. Install Dependencies
```bash
pip install -r requirements.txt
```
3. Add .env with your Gemini API key:
```bash
GEMINI_API_KEY=your_api_key_here
```

4. Run the app
```bash
python app.py
```
Visit http://localhost:5000

📁 Structure
```bash
app.py            # Flask backend
templates/
  index.html      # Frontend UI
static/
  script.js       # JS logic
  style.css       # Styles
uploads/          # Uploaded files
.env              # API Key
```
[![Try Live Demo](https://img.shields.io/badge/Try%20Live%20Demo-%F0%9F%9A%80-blue?style=for-the-badge)](https://resume-demo.onrender.com)

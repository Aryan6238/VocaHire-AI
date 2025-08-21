# =====================================================
#  VocaHire AI - Voice-based Mock Interview System
# =====================================================

# 🚀 Project Overview
# VocaHire AI is a voice-interactive mock interview system
# built with Flask, Hugging Face, and OpenAI Whisper.
# It analyzes resumes, generates AI-driven interview questions,
# records candidate responses, provides feedback, and asks follow-ups.

# ✨ Features
# - Resume Parsing (extracts key skills & experience)
# - AI-Powered Question Generation
# - Text-to-Speech (TTS) for asking questions
# - Browser-based Voice Recording for answers
# - Whisper Speech-to-Text transcription
# - AI Feedback on candidate responses
# - Smart Follow-up Questions

# 🛠️ Tech Stack
# - Backend: Flask (Python)
# - AI Models: Hugging Face (GLM / LLMs), Whisper
# - Frontend: HTML + CSS + JavaScript
# - Audio: Web Audio API, gTTS / pyttsx3
# - Version Control: Git + GitHub

# 📂 Project Structure
# ├── app.py                 # Flask backend
# ├── requirements.txt       # Dependencies
# ├── uploads/               # Resume uploads
# ├── frontend/
# │   ├── static/
# │   │   └── audio/         # Saved audio responses
# │   └── templates/
# │       └── index.html     # Main UI
# ├── models/                # AI models & pipelines
# ├── resume_parser/         # Resume parsing logic
# ├── voice_processor/       # Audio handling
# └── question_gen/          # Question + follow-up generation

# ⚙️ Setup Instructions
# Clone the repository
git clone https://github.com/Aryan6238/VocaHire-AI.git
cd VocaHire-AI

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate   # On Linux/Mac
venv\Scripts\activate      # On Windows

# Install dependencies
pip install -r requirements.txt

# Run the Flask app
python app.py

# Open in browser
# http://127.0.0.1:5000/

# 🤖 How It Works
# 1. Upload Resume → Extracts skills & experience
# 2. AI Generates Questions → Displays & plays via TTS
# 3. Candidate Records Answer → Audio saved locally
# 4. Whisper Transcribes → Converts speech → text
# 5. AI Feedback → Provides review of response
# 6. Follow-up Questions → Dynamically generated if needed

# 📈 Future Enhancements
# - Multi-language interview support
# - AI scoring system (candidate ranking)
# - Dashboard for interview analytics
# - Cloud deployment with Docker

# 🧑‍💻 Author
# Aryan Vishal Jalak
# B.Tech CSE (AI & Analytics), MIT ADT University, Pune

# 📜 License
# MIT License

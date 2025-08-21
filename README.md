# VocaHire AI 🎙️🤖

AI-powered voice-based mock interviewer designed to help candidates prepare for real-world interviews.  
It analyzes resumes, asks intelligent questions, records answers, provides feedback, and generates follow-up questions — all in real-time.

------------------------------------------------------------
🚀 Features
------------------------------------------------------------
- 📄 Resume Parsing: Extracts key details from resumes.
- 🎤 Voice Interaction: Converts questions to speech and records candidate answers.
- ✍️ Answer Analysis: Transcribes speech to text and reviews answers.
- 🔄 Follow-up Questions: Generates dynamic follow-ups based on responses.
- 🌐 Web-based UI: Simple, interactive frontend with one-question-at-a-time flow.
- 📊 Feedback: Provides separate review for each answer.

------------------------------------------------------------
🛠️ Tech Stack
------------------------------------------------------------
- Backend: Flask (Python)
- Frontend: HTML, CSS, JavaScript
- NLP Models: Hugging Face Transformers
- TTS: gTTS / pyttsx3
- STT: OpenAI Whisper
- Storage: Local (audio & resumes)
- Version Control: Git & GitHub

------------------------------------------------------------
📂 Project Structure
------------------------------------------------------------
```
mock_interviewer/
│── app.py                  # Flask backend
│── requirements.txt        # Dependencies
│── uploads/                # Uploaded resumes
│── frontend/
│   ├── index.html          # Main UI
│   ├── static/
│   │   ├── css/            # Styles
│   │   ├── js/             # Scripts
│   │   ├── audio/          # Recorded audio files
│── models/                 # AI/NLP models
│── resume_parser.py        # Resume parsing logic
│── voice_processor.py      # Audio recording + processing
│── question_gen.py         # Question & follow-up generator
```

------------------------------------------------------------
⚙️ Installation
------------------------------------------------------------
# Clone the repository
git clone https://github.com/your-username/VocaHire-AI.git
cd VocaHire-AI

# Create a virtual environment
python -m venv venv
source venv/bin/activate   # On Mac/Linux
venv\Scripts\activate      # On Windows

# Install dependencies
pip install -r requirements.txt

------------------------------------------------------------
▶️ Usage
------------------------------------------------------------
# Run the Flask app
python app.py

# Open in browser
http://127.0.0.1:5000/

------------------------------------------------------------
📌 Future Improvements
------------------------------------------------------------
- Add multi-language support for interviews
- Advanced AI-driven scoring system
- Cloud deployment (AWS/GCP/Azure)
- Candidate performance dashboard

------------------------------------------------------------
🤝 Contributing
------------------------------------------------------------
Pull requests are welcome!  
For major changes, please open an issue first to discuss what you’d like to change.

------------------------------------------------------------
📜 License
------------------------------------------------------------
MIT License

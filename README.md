<<<<<<< HEAD
AI Mock Interviewer
====================

One-line summary
----------------
An interactive mock interviewer that analyzes a resume, asks voice-based interview questions, records answers, and provides feedback — with client-side webcam proctoring to detect absence or multiple people.

Contents of this README
-----------------------
- Project summary
- Tech stack
- Architecture (see `frontend/templates/architecture.png` or the `architecture.png` you saved)
- Setup & Run (PowerShell commands)
- Quick smoke tests
- APIs & data shapes
- Proctoring and logs
- Demo video & transcript
- Submission checklist
- Known limitations & next steps

Project summary
---------------
This project accepts a resume (PDF), extracts skills and generates interview questions. The user records spoken answers which are processed by the backend for transcription and feedback. A lightweight client-side proctoring component (TFJS + BlazeFace) detects face-count changes and reports events to the backend. Proctor reports are saved as JSON-lines in `uploads/proctor_logs/`.

Tech stack
----------
- Python 3.10
- Flask (backend server)
- Frontend: HTML, CSS, vanilla JavaScript
- Client ML: TensorFlow.js + BlazeFace (browser-side face detection)
- Audio processing: gTTS, pydub , Whisper
- Storage: local `uploads/` directory for audio and logs

- Backend LLM: TinyLlama-1.1B-Chat-v1.0 (Hugging Face transformers; used by `backend/question_gen.py` for question generation)

Architecture
------------
See the architecture diagram file saved.

Setup & Run (PowerShell)
------------------------
These instructions assume Windows PowerShell. Copy-paste lines individually.

Create and activate a virtual environment
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install --upgrade pip
pip install -r requirements.txt
```

Create a `.env` file from `.env.example` and fill values.

(If your project requires DB initialization)
```powershell
python create_db.py
```

Start the Flask application
Option A - run directly (if `backend/app.py` includes app.run):
```powershell
python backend\app.py
```
Option B - flask CLI :
```powershell
$env:FLASK_APP='backend.app'
$env:FLASK_ENV='development'
flask run --host=127.0.0.1 --port=5000
```

Open the application in your browser:
- http://127.0.0.1:5000

Note: Camera access works on `localhost` in most browsers and on HTTPS origins. If you host remotely, use HTTPS.

Quick smoke tests
-----------------
1. Upload a sample resume (PDF) and click "Analyze Resume".
2. Click "Proceed to Camera" → "Enable Webcam" and allow camera permission. The proctor pane should display face count.
3. If a single face is stable, the "Start Interview" (Start Interview) button appears. Start recording, stop and submit. The audio should play and feedback should appear.
4. Check the proctor log file created: `uploads/proctor_logs/proctor_<YYYY-MM-DD>.log` — it should contain JSON-lines for events like `face_count_change`, `absence_detected`, `multiple_faces_detected`.

APIs & data shapes
------------------
- POST /api/analyze-resume
  - Input: multipart/form-data { resume: file }
  - Output: JSON { analysis: { skills: [..] }, questions: [..] }

- POST /api/process-audio
  - Input: multipart/form-data { audio: file, question: string }
  - Output (example):
    {
      "status": "success",
      "transcript": "...",
      "feedback": "...",
      "proficiency": "intermediate",
      "confidence": 0.82,
      "follow_up": "Optional follow up question string"
    }

- POST /api/proctor-report
  - Input: JSON { session_id: string, event: string, timestamp: ISO, details: object }
  - Behavior: Appends a newline-delimited JSON entry to `uploads/proctor_logs/proctor_<date>.log`.

Proctoring and logs
-------------------
- The client-side proctoring is implemented with TensorFlow.js + BlazeFace. It sends compact JSON events to `/api/proctor-report` describing face-count changes and suspicious conditions.
- Logs are newline-delimited JSON objects. Example entry:
  {"session_id":"168...","event":"multiple_faces_detected","timestamp":"2025-11-19T10:20:30.123Z","details":{"faces":2}}

-------------------
- README.md (this file)
- demo.mp4 (3–6 minutes)
- Architecture_Diag.pdf (diagram)
- .env.example


Known limitations & next steps
-----------------------------
- Proctoring: currently client-only detection and compact event logging; no image or video evidence is uploaded to protect privacy. If required, a toggle to capture encrypted thumbnails can be added.
- Scalability: The current app stores uploads locally; for production consider S3 (or similar) and a managed DB for state.
- Improvements: better offline resilience, configurable detection sensitivity, admin dashboard for reviewing proctor logs.

---
=======
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
```
git clone https://github.com/your-username/VocaHire-AI.git
cd VocaHire-AI
```
# Create a virtual environment
```
python -m venv venv
source venv/bin/activate   # On Mac/Linux
venv\Scripts\activate      # On Windows
```
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
>>>>>>> d5149f326e8f0ab22c2dfa1ba991c11400a0bf57

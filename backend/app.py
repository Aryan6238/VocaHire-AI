from flask import Flask, request, jsonify, send_file, render_template
from flask_cors import CORS
from voice_processor import AudioTranscriber
from resume_parser import ResumeParser
from question_gen import QuestionGenerator
from models import db, Interview
from tts_generator import generate_audio_questions
from gtts import gTTS
from pydub import AudioSegment
from datetime import datetime
import os
import uuid
import json
import re

# ------------------- CONFIG -------------------
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
AUDIO_FOLDER = os.path.join(BASE_DIR, '../frontend/static/audio')

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(AUDIO_FOLDER, exist_ok=True)

# ------------------- FLASK INIT -------------------
app = Flask(
    __name__,
    static_folder='../frontend/static',
    template_folder='../frontend/templates'
)
CORS(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///interviews.db'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

db.init_app(app)

# ------------------- MODULE INIT -------------------
transcriber = AudioTranscriber()
resume_parser = ResumeParser()
question_gen = QuestionGenerator()

# ------------------- CONSTANTS -------------------
MIN_ANSWER_LENGTH = 5  # Minimum words to be considered valid answer
TECHNICAL_TERMS = [
    'algorithm', 'database', 'API', 'framework', 'JavaScript', 'Python', 
    'React', 'Node.js', 'machine learning', 'AI', 'cloud', 'devops',
    'backend', 'frontend', 'fullstack', 'container', 'microservices',
    'CI/CD', 'agile', 'scrum', 'OOP', 'REST', 'GraphQL', 'SQL', 'NoSQL',
    'Docker', 'Kubernetes', 'AWS', 'Azure', 'GCP', 'neural network',
    'deep learning', 'natural language processing', 'computer vision'
]

FILLER_WORDS = ['um', 'uh', 'like', 'you know', 'so', 'well', 'basically', 'actually']

# ------------------- ROUTES -------------------

@app.route('/')
def home():
    return render_template('index.html')

# ----------- Resume Upload and Analysis -----------
@app.route('/api/analyze-resume', methods=['POST'])
def analyze_resume():
    try:
        if 'resume' not in request.files:
            return jsonify({"error": "No resume file provided"}), 400

        file = request.files['resume']
        if not file.filename.endswith('.pdf'):
            return jsonify({"error": "Only PDF files are allowed"}), 400

        filename = f"resume_{datetime.now().timestamp()}.pdf"
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)
        print(f"✅ Resume saved: {filepath}")

        analysis = resume_parser.analyze(filepath)
        print(f"✅ Resume parsed: {analysis}")

        if not analysis or not analysis.skills:
            raise Exception("Resume parsing failed or returned empty data")

        resume_summary = " ".join(analysis.skills + analysis.education + analysis.experience)
        raw_questions = question_gen.generate(resume_summary)
        print(f"✅ Raw questions generated: {raw_questions}")

        # Clean and validate questions
        questions = []
        for q in raw_questions:
            # Skip introductory statements
            if "here are the" in q.lower() or "based on" in q.lower():
                continue
                
            # Remove numbering/lettering (a., b., 1., etc.)
            q = re.sub(r'^[a-zA-Z0-9]+[.)]\s*', '', q).strip()
            
            # Skip statements that aren't questions
            if not q.endswith('?'):
                continue
                
            # Remove duplicate question marks
            q = q.rstrip('?') + '?'
            
            # Ensure minimum question length
            if len(q.split()) >= 3:  # At least 3 words
                questions.append(q)
        
        # Fallback if cleaning removed all questions
        if not questions:
            questions = [
                "Can you explain your experience with the technologies mentioned in your resume?",
                "What was your most challenging technical project?",
                "How do you approach problem-solving in your work?"
            ]

        print(f"✅ Cleaned questions: {questions[:5]}")

        # Generate audio for each valid question
        generate_audio_questions(questions[:5], output_dir=AUDIO_FOLDER)

        # Combine audio with proper padding
        combined_audio = AudioSegment.silent(duration=500)  # Initial padding
        for i in range(min(5, len(questions))):
            wav_file = os.path.join(AUDIO_FOLDER, f"question_{i+1}.wav")
            try:
                audio = AudioSegment.from_wav(wav_file)
                combined_audio += audio + AudioSegment.silent(duration=1000)  # 1s between questions
            except Exception as e:
                print(f"⚠️ Error loading question {i+1}: {e}")
                continue

        final_audio_path = os.path.join(AUDIO_FOLDER, "questions.mp3")
        combined_audio.export(final_audio_path, format="mp3")
        print(f"✅ Final audio saved: {final_audio_path}")

        interview = Interview(
            resume_path=filepath,
            questions=", ".join(questions[:5])  # Store cleaned questions
        )
        db.session.add(interview)
        db.session.commit()

        return jsonify({
            "status": "success",
            "analysis": analysis.__dict__,
            "questions": questions[:5],
            "audio_url": "/static/audio/questions.mp3"
        })

    except Exception as e:
        print(f"❌ Error in analyze_resume: {e}")
        return jsonify({"error": str(e)}), 500
    
# ----------- Process Recorded Answer and Generate Follow-Up -----------
@app.route('/api/process-audio', methods=['POST'])
def process_audio():
    try:
        if 'audio' not in request.files:
            return jsonify({"error": "No audio file provided"}), 400

        file = request.files['audio']
        current_question = request.form.get('question', '')
        filename = f"answer_{datetime.now().timestamp()}.wav"
        filepath = os.path.join(AUDIO_FOLDER, filename)
        file.save(filepath)
        print(f"✅ Answer audio saved: {filepath}")

        # Transcribe the audio
        transcript_result = transcriber.transcribe(filepath)
        print(f"📝 Full Whisper Output: {transcript_result}")

        transcript_text = transcript_result['text'].strip()
        if not transcript_text:
            return jsonify({"error": "Transcription failed or empty"}), 500

        # Generate comprehensive feedback
        feedback_data = generate_comprehensive_feedback(current_question, transcript_text)
        
        # Generate audio responses
        audio_responses = generate_audio_responses(transcript_text, feedback_data['follow_up'])

        return jsonify({
            "status": "success",
            "transcript": transcript_text,
            "feedback": feedback_data['feedback'],
            "follow_up": feedback_data['follow_up'],
            "expected_answer": feedback_data['expected_answer'],
            "proficiency": feedback_data['proficiency'],
            "confidence": feedback_data['confidence'],
            "improvement_suggestions": feedback_data['improvement_suggestions'],
            "followup_audio": audio_responses['followup_audio'],
            "you_said_audio": audio_responses['you_said_audio']
        })

    except Exception as e:
        print(f"❌ Error in process_audio: {e}")
        return jsonify({"error": str(e)}), 500

def generate_comprehensive_feedback(question, answer):
    """Generate detailed feedback with scores and expected answer"""
    # Validate answer length first
    word_count = len(answer.split())
    if word_count < MIN_ANSWER_LENGTH:
        return {
            "feedback": "Your answer is too brief. Please elaborate with technical details and examples.",
            "proficiency": max(10, min(30, word_count * 5)),  # 10-30% for very short answers
            "confidence": max(10, min(30, word_count * 5)),
            "expected_answer": generate_expected_answer_template(question),
            "follow_up": "",
            "improvement_suggestions": [
                "Provide more technical details",
                "Include specific examples",
                "Explain your thought process"
            ]
        }

    # Generate follow-up question (context-aware)
    follow_up = question_gen.generate_follow_up(
        f"Question: {question}\nAnswer: {answer}"
    )
    
    # Generate specific feedback analyzing the answer
    feedback_prompt = f"""
    Analyze this interview Q&A and provide specific feedback:
    - Technical accuracy (0-100)
    - Relevance to question (0-100)
    - Communication clarity (0-100)
    - 3 specific improvement suggestions
    
    Question: {question}
    Answer: {answer}
    
    Return as JSON with: feedback, proficiency, confidence, expected_answer, improvement_suggestions
    """
    
    try:
        feedback_response = question_gen.generate(feedback_prompt)
        feedback_data = json.loads(feedback_response)
    except Exception as e:
        print(f"⚠️ Feedback generation error: {e}")
        feedback_data = generate_fallback_feedback(question, answer)
    
    # Ensure all required fields exist with proper validation
    feedback_data.setdefault('feedback', generate_dynamic_feedback(answer))
    feedback_data.setdefault('proficiency', calculate_proficiency(answer))
    feedback_data.setdefault('confidence', calculate_confidence(answer))
    feedback_data.setdefault('expected_answer', generate_expected_answer_template(question))
    feedback_data.setdefault('improvement_suggestions', [
        "Provide more technical details",
        "Include specific examples",
        "Structure your answer more clearly"
    ])
    feedback_data['follow_up'] = follow_up
    
    # Validate scores are within bounds
    feedback_data['proficiency'] = max(0, min(100, feedback_data['proficiency']))
    feedback_data['confidence'] = max(0, min(100, feedback_data['confidence']))
    
    return feedback_data

def generate_fallback_feedback(question, answer):
    """Generate feedback when the main generation fails"""
    word_count = len(answer.split())
    base_score = min(70, max(30, word_count * 2))  # 30-70% range
    
    return {
        "feedback": "Your answer was received. Here's some feedback: " + (
            "Good technical content but could use more structure." if word_count > 20 
            else "Try to elaborate more with specific examples."
        ),
        "proficiency": base_score,
        "confidence": base_score - 10,
        "expected_answer": generate_expected_answer_template(question),
        "improvement_suggestions": [
            "Provide more technical details",
            "Include specific examples",
            "Explain your thought process"
        ]
    }

def generate_dynamic_feedback(answer):
    """Generate context-aware feedback based on answer content"""
    tech_term_count = count_technical_terms(answer)
    word_count = len(answer.split())
    
    if tech_term_count >= 5 and word_count > 30:
        return "Strong technical answer! Consider adding more real-world examples."
    elif tech_term_count >= 3:
        return "Good technical content. Try to better connect concepts to the question."
    else:
        return "Focus on including more technical terms and specific examples."

def generate_expected_answer_template(question):
    """Generate a structured expected answer template"""
    return {
        "structure": [
            "Clear definition of key terms",
            "2-3 main advantages or applications",
            "Specific examples or case studies",
            "Relevance to industry trends"
        ],
        "content": f"A strong answer to '{question}' would:",
        "examples": [
            "Reference specific technologies",
            "Include measurable outcomes",
            "Demonstrate problem-solving approach"
        ]
    }

def calculate_proficiency(answer):
    """Calculate technical proficiency score (0-100)"""
    tech_terms = count_technical_terms(answer)
    word_count = len(answer.split())
    
    # Base score based on technical term density
    term_density = (tech_terms / (word_count + 1)) * 100
    base_score = min(70 + (term_density * 0.3), 95)  # 70-95 range
    
    # Adjust for answer length
    length_adjustment = min(word_count / 50 * 10, 10)  # Up to +10 for longer answers
    return min(int(base_score + length_adjustment), 100)

def calculate_confidence(answer):
    """Calculate speaking confidence score (0-100)"""
    fillers = count_filler_words(answer)
    word_count = len(answer.split())
    
    # Base score based on filler word frequency
    filler_rate = (fillers / (word_count + 1)) * 100
    base_score = max(50, 90 - (filler_rate * 2))  # 50-90 range
    
    # Adjust for sentence structure
    sentence_count = len(re.split(r'[.!?]', answer))
    if sentence_count > 0:
        avg_sentence_length = word_count / sentence_count
        if 10 <= avg_sentence_length <= 20:
            base_score += 5  # Bonus for ideal sentence length
    
    return min(int(base_score), 100)

def generate_audio_responses(transcript, follow_up):
    """Generate both 'You said' and follow-up question audio"""
    you_said_text = f"You said: {transcript}"
    followup_text = f"Follow-up question: {follow_up}"

    you_said_filename = f"you_said_{uuid.uuid4()}.mp3"
    followup_filename = f"followup_{uuid.uuid4()}.mp3"

    gTTS(you_said_text).save(os.path.join(AUDIO_FOLDER, you_said_filename))
    gTTS(followup_text).save(os.path.join(AUDIO_FOLDER, followup_filename))

    return {
        "followup_audio": f"/static/audio/{followup_filename}",
        "you_said_audio": f"/static/audio/{you_said_filename}"
    }

def count_technical_terms(text):
    """Count domain-specific terms in answer"""
    return sum(text.lower().count(term.lower()) for term in TECHNICAL_TERMS)

def count_filler_words(text):
    """Count filler words in transcript"""
    return sum(text.lower().count(filler) for filler in FILLER_WORDS)

# [Rest of your routes remain unchanged...]

<<<<<<< HEAD

# ----------- Proctoring Report Endpoint -----------
@app.route('/api/proctor-report', methods=['POST'])
def proctor_report():
    """Receive proctoring reports from the frontend and save to a log file.

    Expects JSON: { session_id, event, timestamp, details }
    """
    try:
        data = request.get_json(force=True)
        if not data:
            return jsonify({"error": "No JSON body provided"}), 400

        # Ensure proctor log folder exists
        proctor_dir = os.path.join(app.config.get('UPLOAD_FOLDER', 'uploads'), 'proctor_logs')
        os.makedirs(proctor_dir, exist_ok=True)

        # Normalize and enrich report
        report = {
            "session_id": data.get('session_id'),
            "event": data.get('event'),
            "timestamp": data.get('timestamp') or datetime.now().isoformat(),
            "details": data.get('details', {})
        }

        # Use a per-day log file and append JSON lines for easy ingestion
        logfile = os.path.join(proctor_dir, f"proctor_{datetime.now().date()}.log")
        with open(logfile, 'a', encoding='utf-8') as f:
            f.write(json.dumps(report) + "\n")

        print(f"✅ Proctor report saved: {report}")
        return jsonify({"status": "ok"})
    except Exception as e:
        print(f"❌ Error in proctor_report: {e}")
        return jsonify({"error": str(e)}), 500

=======
>>>>>>> d5149f326e8f0ab22c2dfa1ba991c11400a0bf57
# ------------------- RUN APP -------------------
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
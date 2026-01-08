// Resume Upload and Initial Question Generation
document.getElementById('analyzeBtn').addEventListener('click', async () => {
    const file = document.getElementById('resumeUpload').files[0];
    if (!file) return alert("Please upload a resume");

    const formData = new FormData();
    formData.append('resume', file);

    try {
        const response = await fetch('/api/analyze-resume', {
            method: 'POST',
            body: formData
        });
        const data = await response.json();
        initializeQuestionFlow(data.questions);
        displayResumeResults(data);
    } catch (err) {
        console.error(err);
        alert("Error analyzing resume");
    }
});

// State Variables
let currentQuestionIndex = 0;
let questions = [];

// Initialize Flow
function initializeQuestionFlow(fetchedQuestions) {
    questions = fetchedQuestions;
    currentQuestionIndex = 0;
    showQuestion(questions[currentQuestionIndex]);
}

// Show Current Question
function showQuestion(questionText) {
    const questionDisplay = document.getElementById('questionDisplay');
    questionDisplay.innerHTML = `
        <h3>Question ${currentQuestionIndex + 1}:</h3>
        <p>${questionText}</p>
        <button id="playQuestionAudio">🔊 Play Question</button>
        <button id="recordBtn">🎙️ Start Recording</button>
        <div id="feedbackDisplay"></div>
    `;

    document.getElementById('playQuestionAudio').addEventListener('click', () => {
        playQuestionAudio(questionText);
    });

    document.getElementById('recordBtn').addEventListener('click', () => {
        if (!mediaRecorder) {
            startRecording();
        } else {
            stopRecording();
        }
    });
}

// TTS: Play Question Audio
function playQuestionAudio(questionText) {
    fetch('/api/text-to-speech', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: questionText })
    })
    .then(response => response.json())
    .then(data => {
        const audio = new Audio(data.audio_url);
        audio.play();
    })
    .catch(err => {
        console.error('Error playing audio:', err);
    });
}

// Audio Recording
let mediaRecorder;
let audioChunks = [];

async function startRecording() {
    try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        mediaRecorder = new MediaRecorder(stream);

        mediaRecorder.ondataavailable = e => {
            audioChunks.push(e.data);
        };

        mediaRecorder.onstop = async () => {
            const audioBlob = new Blob(audioChunks, { type: 'audio/mp3' });
            await processRecording(audioBlob);
            audioChunks = [];
        };

        mediaRecorder.start();
        document.getElementById('recordBtn').textContent = "⏹️ Stop Recording";
    } catch (err) {
        alert("Microphone access denied");
    }
}

function stopRecording() {
    mediaRecorder.stop();
    mediaRecorder = null;
    document.getElementById('recordBtn').textContent = "🎙️ Start Recording";
}

// Submit Answer and Get Feedback + Follow-up
async function processRecording(audioBlob) {
    const formData = new FormData();
    formData.append('audio', audioBlob, `response_q${currentQuestionIndex + 1}.mp3`);

    try {
        const response = await fetch('/api/process-audio', {
            method: 'POST',
            body: formData
        });
        const data = await response.json();
        
        // Display feedback and follow-up
        displayFeedback(data);

        // Create Next Question button if it doesn't exist
        let nextBtn = document.getElementById('nextBtn');
        if (!nextBtn) {
            nextBtn = document.createElement('button');
            nextBtn.id = 'nextBtn';
            nextBtn.textContent = 'Next Question ➡️';
            nextBtn.addEventListener('click', nextQuestion);
            document.getElementById('questionDisplay').appendChild(nextBtn);
        }

        // Handle follow-up question
        if (data.follow_up) {
            const followUpQuestion = data.follow_up;
            if (!questions.includes(followUpQuestion)) {
                questions.splice(currentQuestionIndex + 1, 0, followUpQuestion);
            }

            // Play follow-up audio if available
            if (data.followup_audio) {
                const followAudio = new Audio(data.followup_audio);
                followAudio.play();
            }
        }

    } catch (err) {
        console.error(err);
        alert("Error processing audio response");
    }
}

// Move to Next Question
function nextQuestion() {
    currentQuestionIndex++;
    if (currentQuestionIndex < questions.length) {
        showQuestion(questions[currentQuestionIndex]);
    } else {
        document.getElementById('questionDisplay').innerHTML = `<h3>🎉 Interview Complete!</h3>`;
    }
}

// Resume Results Display
function displayResumeResults(data) {
    const container = document.getElementById('resumeResults');
    container.innerHTML = `
        <h3>Skills Found:</h3>
        <ul>${data.analysis.skills.map(s => `<li>${s}</li>`).join('')}</ul>
        <h3>Suggested Questions:</h3>
        <ol>${data.questions.map(q => `<li>${q}</li>`).join('')}</ol>
    `;
}

// Feedback Display
function displayFeedback(data) {
    const container = document.getElementById('feedbackDisplay');
    
    // Check if feedback is string or object
    let feedbackContent;
    if (typeof data.feedback === 'string') {
        feedbackContent = `<p>${data.feedback}</p>`;
    } else {
        feedbackContent = `
            <p><strong>Filler Words:</strong> ${data.feedback.filler_words || 'N/A'}</p>
            <p><strong>Speech Rate:</strong> ${data.feedback.speech_rate ? data.feedback.speech_rate.toFixed(2) : 'N/A'} words/sec</p>
            <p><strong>Suggestions:</strong> ${data.feedback.suggestions || 'N/A'}</p>
        `;
    }

    container.innerHTML = `
        <h4>🗣️ Transcript:</h4>
        <p>${data.transcript}</p>
        <h4>🔍 Feedback:</h4>
        ${feedbackContent}
    `;

    if (data.follow_up) {
        container.innerHTML += `
            <h4>📌 Follow-Up Question:</h4>
            <p>${data.follow_up}</p>
        `;
    }
}

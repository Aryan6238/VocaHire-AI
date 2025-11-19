import os
from TTS.api import TTS

tts = TTS(model_name="tts_models/en/ljspeech/tacotron2-DDC", progress_bar=False)

def generate_audio_questions(questions, output_dir="static/audio_questions"):
    os.makedirs(output_dir, exist_ok=True)
    audio_files = []

    for i, question in enumerate(questions):
        filename = f"question_{i+1}.wav"
        filepath = os.path.join(output_dir, filename)
        tts.tts_to_file(text=question, file_path=filepath)
        audio_files.append(filepath)

    return audio_files

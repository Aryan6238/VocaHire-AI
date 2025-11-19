import whisper
from typing import Dict, Any, List


class AudioTranscriber:
    def __init__(self, model_size: str = "base"):
        """
        Initialize the Whisper model for audio transcription.
        :param model_size: Size of the Whisper model to load (e.g., "base", "small", "medium", "large").
        """
        self.model = whisper.load_model(model_size)

    def transcribe(self, audio_path: str) -> Dict[str, Any]:
        """
        Transcribe the audio file and return the result with timestamps and language.
        :param audio_path: Path to the input audio file.
        :return: Dictionary containing transcribed text, detected language, and word-level timestamps.
        """
        try:
            result = self.model.transcribe(audio_path, word_timestamps=True)
            words = [word for segment in result.get("segments", []) for word in segment.get("words", [])]

            return {
                "text": result.get("text", "").strip(),
                "language": result.get("language", "unknown"),
                "words": words
            }
        except Exception as e:
            print(f"❌ Transcription failed: {str(e)}")
            return {
                "text": "",
                "language": "error",
                "words": []
            }

    def analyze(self, transcription: Dict[str, Any]) -> Dict[str, float]:
        """
        Analyze the transcribed speech for filler words, speech rate, and minimum confidence.
        :param transcription: Transcription result from `transcribe` method.
        :return: Dictionary containing analysis metrics.
        """
        words: List[Dict[str, Any]] = transcription.get("words", [])
        if not words:
            return {
                "filler_words": 0,
                "speech_rate": 0.0,
                "confidence": 0.0
            }

        try:
            # Count filler words
            filler_words = sum(1 for w in words if w["word"].lower() in {"um", "uh"})

            # Calculate duration
            duration = words[-1]["end"] - words[0]["start"]
            speech_rate = len(words) / duration if duration > 0 else 0.0

            # Confidence (minimum probability)
            confidence = min(w.get("probability", 1.0) for w in words)

            return {
                "filler_words": filler_words,
                "speech_rate": round(speech_rate, 2),
                "confidence": round(confidence, 3)
            }

        except Exception as e:
            print(f"❌ Audio analysis failed: {str(e)}")
            return {
                "filler_words": 0,
                "speech_rate": 0.0,
                "confidence": 0.0
            }

from faster_whisper import WhisperModel
from lib.IO_ENV import INPUT_FILE

model = WhisperModel("medium", device="cuda", compute_type="float16")

def transcribe(audio_path: str) -> str:
    segments, _ = model.transcribe(audio_path)

    return " ".join([segment.text for segment in segments])
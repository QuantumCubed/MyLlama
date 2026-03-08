from faster_whisper import WhisperModel
from lib.IO_ENV import INPUT_FILE
import numpy as np

model = WhisperModel("medium", device="cuda", compute_type="float16")

def transcribe(audio: bytes) -> str:
    segments, _ = model.transcribe(np.frombuffer(audio, dtype=np.float16))
    
    return " ".join([segment.text for segment in segments])
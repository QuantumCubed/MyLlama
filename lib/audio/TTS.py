from kokoro import KPipeline
import soundfile as sf
import io
import torch
import numpy as np
from fastapi import WebSocket

# pipeline = KPipeline(lang_code="a")
pipeline = KPipeline(lang_code="a", device="cuda")

def synthesize_speech(text: str) -> bytes:
    chunks = []
    for _, _, audio in pipeline(text, voice="af_heart"):
        if isinstance(audio, torch.Tensor):
            chunks.append(audio.cpu().numpy())
    
    audio_array = np.concatenate(chunks, axis=0)
    pcm = (audio_array * 32767).astype(np.int16) # PCM_16 conversion (PCM_S16LE)
    return pcm.tobytes()

async def synthesize_speech_stream(text: str, websocket: WebSocket) -> None:
    chunks = []
    for _, _, audio in pipeline(text, voice="af_heart"):
        if isinstance(audio, torch.Tensor):
            pcm = (audio.cpu().numpy() * 32767).astype(np.int16) # PCM_16 conversion (PCM_S16LE)

            await websocket.send_bytes(pcm.tobytes())
    

# 24000Hz
# 16-bit
# 4096 - 8192 samples per chunk
# mono (1) channel
from typing import Sequence, cast

from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv
from lib.audio import STT, TTS, Audio_IO
from lib.chat.LLM_Operations import LLM_OPS
from lib.schema import PySchemas
from lib.utils import string_utils
from lib.integrations.IoT import HomeAssistantWebSocket
from contextlib import asynccontextmanager
from lib.tools.Tool_Functions import ExternalTools
from fastapi.responses import StreamingResponse
import tempfile
import os

load_dotenv()

MODEL = LLM_OPS()
HA = HomeAssistantWebSocket()

@asynccontextmanager
async def lifespan(app: FastAPI):

    # init HomeAssistant WebSocket

    await HA.connect()

    TOOLS = ExternalTools(HA)
    MODEL.init_tools(TOOLS)

    yield

    await HA.disconnect()

    # init DB Connection

app = FastAPI(lifespan=lifespan)

@app.post("/chat")
async def call_model(req: PySchemas.OllamaRequest):
    return StreamingResponse(MODEL.chat(req.prompt), media_type="text/plain")

# maybe switch to PCM for audio instead of WAV?
# SWITCH BACK TO .POST WHEN ABLE
# need to cleanup response text from LLM (ast, md, etc,)
@app.post("/chat-audio")
async def call_model_audio(audio: UploadFile = File(...)):

    audio_bytes = await audio.read()

    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        tmp.write(audio_bytes)
        tmp_path = tmp.name

    prompt: str = STT.transcribe(tmp_path)

    os.unlink(tmp_path)

    async def generate_audio_stream():
        sentence_buffer = ""
        first_chunk = True

        async for chunk in MODEL.chat(prompt):
            sentence_buffer += chunk

            if any(sentence_buffer.endswith(p) for p in [".", "!", "?", "\n"]):
                audio_bytes = TTS.synthesize_speech(sentence_buffer.strip())
                # print(f"Audio bytes length: {len(audio_bytes)}")
                # print(f"First 4 bytes: {audio_bytes[:4]}")
                # print(sentence_buffer)
                sentence_buffer = ""
                
                if first_chunk:
                    yield audio_bytes
                    first_chunk = False
                else:
                    yield audio_bytes[44:]

        if sentence_buffer.strip():
            audio_bytes = TTS.synthesize_speech(sentence_buffer.strip())
            yield audio_bytes[44:] if not first_chunk else audio_bytes

    return StreamingResponse(generate_audio_stream(), media_type="audio/wav")

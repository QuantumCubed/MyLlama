import os, mimetypes
from typing import Sequence, cast

from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.staticfiles import StaticFiles
from openai import AsyncOpenAI
from dotenv import load_dotenv
from lib.audio import XTT, TTX, Audio_IO
from lib.chat.LLM_Operations import LLM_OPS
from lib.schema import PySchemas
from lib.utils import string_utils

load_dotenv()

# Ensure right MIME types
mimetypes.add_type("application/vnd.apple.mpegurl", ".m3u8")
mimetypes.add_type("audio/aac", ".aac")

model = LLM_OPS()

app = FastAPI()

app.mount("/hls", StaticFiles(directory="out/hls"), name="hls")

@app.post("/chat")
async def call_model(req: PySchemas.OllamaRequest):
    return await model.chat(req.prompt)

@app.post("/chat-audio")
async def call_model_audio(audio_file: UploadFile = File(...)):

    # Optional: validate MIME type
    if not (audio_file.content_type or "").startswith("audio/"):
        raise HTTPException(status_code=415, detail="Expected an audio/* file")
    
    await Audio_IO.write_audio_file(audio_file)
    
    req_prompt = XTT.synthesize_text()

    response = await model.chat(req_prompt)
        
    TTX.synthesize_speech(string_utils.clean_text(response))

    await Audio_IO.write_HLS_chunks()

    return "SUCCESS!"
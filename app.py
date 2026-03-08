from typing import AsyncGenerator, Sequence, cast

from fastapi import FastAPI, HTTPException, UploadFile, File, WebSocket
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv
from lib.audio import STT, TTS, Audio_IO
from lib.chat.LLM_Operations import LLM_OPS
from lib.schema import PySchemas
from lib.utils import string_utils
from lib.integrations.home.IoT import HomeAssistantWebSocket
from contextlib import asynccontextmanager
from lib.tools.Tool_Functions import ExternalTools
from fastapi.responses import StreamingResponse
import tempfile
import os
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

MODEL = LLM_OPS()
HA = HomeAssistantWebSocket()

@asynccontextmanager
async def lifespan(app: FastAPI):

    # init HomeAssistant WebSocket

    await HA.connect()

    # EVENTUALLY TIE HA WEBSOCKET TO APP STATE INSTEAD OF GLOBAL IMPORT

    TOOLS = ExternalTools(HA)
    MODEL.init_tools(TOOLS)

    yield

    await HA.disconnect()

    # init DB Connection

app = FastAPI(lifespan=lifespan)

origins = [
    "http://localhost:3000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    # add auth for initial handshake
    await websocket.accept()
    # add sequence tracking i.e. id: 1, 2, 3, ...n
    while True:
        msg = await websocket.receive_json()

        match msg["service"]:
            case "ping":
                await websocket.send_json({"service": "pong"})
            case "echo":
                await websocket.send_json({"service": "echo", "message": msg["message"]})
            case "audio_config":
                await websocket.send_json({
                    "type": "audio_config",
                    "sample_rate": 24000,
                    "bit_depth": 16,
                    "channels": 1,
                    "encoding": "pcm_s16le"
                })
            case "chat":

                prompt: str = msg["prompt"] if not None else ""

                response = await MODEL.route(prompt)

                await websocket.send_json({"chat": "start"})

                if response[0] and isinstance(response[1], AsyncGenerator):
                    async for chunk in response[1]:
                        await websocket.send_text(chunk)
                elif isinstance(response[1], str):
                    await websocket.send_text(response[1])

                await websocket.send_json({"chat": "end"})

            case "audio_chat":
                # audio_bytes = TTS.synthesize_speech(msg["message"])

                # with open("test.pcm", "wb") as f:
                #     f.write(audio_bytes)

                audio_data = await websocket.receive_bytes()

                prompt = STT.transcribe(audio_data)

                response = await MODEL.route(prompt)

                await websocket.send_json({"chat": "start"})

                if response[0] and isinstance(response[1], AsyncGenerator): 
                    sentence_buffer = ""

                    async for chunk in response[1]:
                        sentence_buffer += chunk

                        if any(sentence_buffer.endswith(p) for p in [".", "!", "?", "\n"]):
                            await TTS.synthesize_speech_stream(sentence_buffer.strip(), websocket)
                            sentence_buffer = ""
                    
                    if sentence_buffer.strip():
                        await TTS.synthesize_speech_stream(sentence_buffer.strip(), websocket)

                elif isinstance(response[1], str):
                    await TTS.synthesize_speech_stream(response[1], websocket)

                await websocket.send_json({"chat": "end"})


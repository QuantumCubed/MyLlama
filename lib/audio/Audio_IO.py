import aiofiles
from fastapi import File, UploadFile
from lib.audio import FFMPEG_Transcode
from lib.IO_ENV import INPUT_FILE, OUTPUT_FILE, OUTPUT_STREAM_DIR

async def write_audio_file(audio_file: UploadFile = File(...)):
    async with aiofiles.open(INPUT_FILE, "wb") as out:
            while True:
                chunk = await audio_file.read(1024 * 1024) # 1 MB
                if not chunk:
                    break
                await out.write(chunk)

async def write_HLS_chunks():
     await FFMPEG_Transcode.wav_to_hls(OUTPUT_FILE, OUTPUT_STREAM_DIR)
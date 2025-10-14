from pathlib import Path
import subprocess

async def wav_to_hls(input_path: str, output_dir: str):

    Path(output_dir).mkdir(parents=True, exist_ok=True)

    cmd = [
        "ffmpeg",
        "-i", input_path,
        "-ac", "2",          # stereo
        "-ar", "48000",      # 48 kHz
        "-c:a", "aac",       # codec
        "-b:a", "128k",      # bitrate
        "-f", "hls",
        "-hls_time", "4",    # 4 second segments
        "-hls_playlist_type", "vod",
        "-hls_segment_filename", f"{output_dir}/seg_%03d.aac",
        f"{output_dir}/playlist.m3u8"
    ]

    subprocess.run(cmd, check=True)
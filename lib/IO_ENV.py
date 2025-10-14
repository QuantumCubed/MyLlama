import os


BASE_DIR = os.path.dirname(__file__)
VOICE_DIR = os.path.abspath(os.path.join(BASE_DIR, "../", "voice"))
VOICE_FILE = os.path.join(VOICE_DIR, "en_GB-cori-high.onnx")
CONFIG_FILE = os.path.join(VOICE_DIR, "en_GB-cori-high.onnx.json")
INPUT_FILE = os.path.abspath(os.path.join(BASE_DIR, "../", "audio-input", "request.m4a"))
OUTPUT_FILE = os.path.abspath(os.path.join(BASE_DIR, "../", "out", "response.wav"))
OUTPUT_STREAM_DIR = os.path.abspath(os.path.join(BASE_DIR, "../", "out", "hls"))
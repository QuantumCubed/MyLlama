from kokoro import KPipeline
import soundfile as sf
import io
import torch

# pipeline = KPipeline(lang_code="a")
pipeline = KPipeline(lang_code="a", device="cuda")

def synthesize_speech(text: str) -> bytes:
    # print(pipeline.voices)
    samples, sample_rate = [], 24000
    for _, _, audio in pipeline(text, voice="af_heart"):
        if isinstance(audio, torch.Tensor):
            # samples.extend(audio.numpy().tolist())
            samples.extend(audio.cpu().numpy().tolist())

    buffer = io.BytesIO()

    sf.write(buffer, samples, sample_rate, format="WAV")
    buffer.seek(0)
    return buffer.getvalue()
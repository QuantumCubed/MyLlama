import wave
from piper import PiperVoice, SynthesisConfig
from lib.IO_ENV import VOICE_FILE, CONFIG_FILE, OUTPUT_FILE

def synthesize_speech(llm_message: str):

    # has a GPU version
    voice = PiperVoice.load(model_path=VOICE_FILE, config_path=CONFIG_FILE)

    # syn_config = SynthesisConfig(
    #     volume=0.5,  # half as loud
    #     length_scale=2.0,  # twice as slow
    #     noise_scale=1.0,  # more audio variation
    #     noise_w_scale=1.0,  # more speaking variation
    #     normalize_audio=False, # use raw audio from voice
    # )

    with wave.open(OUTPUT_FILE, "wb") as wav_file:
        #voice.synthesize_wav("This is a speech synthesis test!", wav_file, syn_config=syn_config)
        voice.synthesize_wav(llm_message, wav_file)
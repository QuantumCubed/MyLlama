import whisper
from lib.IO_ENV import INPUT_FILE

def synthesize_text():

    model = whisper.load_model("base")

    audio_input = whisper.load_audio(INPUT_FILE)
    audio_input = whisper.pad_or_trim(audio_input)

    # make log-Mel spectrogram and move to the same device as the model
    mel = whisper.log_mel_spectrogram(audio_input, n_mels=model.dims.n_mels)

    # detect the spoken language
    _, probs = model.detect_language(mel)

    # decode the audio
    options = whisper.DecodingOptions()
    result = whisper.decode(model, mel, options)

    # print the recognized text
    return result.text # type: ignore
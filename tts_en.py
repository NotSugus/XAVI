import soundfile as sf
from nemo.collections.tts.models.base import SpectrogramGenerator, Vocoder

spec_generator = SpectrogramGenerator.from_pretrained(model_name="tts_en_fastpitch").cuda()
vocoder = Vocoder.from_pretrained(model_name="tts_hifigan").cuda()

parsed = spec_generator.parse("This is an input string.")
spectrogram = spec_generator.generate_spectrogram(tokens=parsed)
audio = vocoder.convert_spectrogram_to_audio(spec=spectrogram)

def AUDIO_EN():
    sf.write("answer.wav", audio.to('cpu').detach().numpy()[0], 22050)
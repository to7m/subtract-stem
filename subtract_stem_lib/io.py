import librosa
import soundfile

from .sanitisation import sanitise_path


def load_audio(path, *, sample_rate=None):
    path = sanitise_path(path)

    audio, sample_rate = librosa.load(path, sr=sample_rate)

    return audio, sample_rate


def save_audio(audio, path, *, sample_rate):
    soundfile.write(path, audio, sample_rate)

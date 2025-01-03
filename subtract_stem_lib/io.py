from fractions import Fraction
import librosa
import soundfile

from .sanitisation import sanitise_path, sanitise_sample_rate


def load_mono_audio(path, *, sample_rate=None):
    path = sanitise_path(path)

    if sample_rate is not None:
        sample_rate = sanitise_sample_rate(sample_rate)

    mono_audio, sample_rate = librosa.load(path, sr=sample_rate)

    mono_audio = sanitise_mono_audio(audio)
    sample_rate = sanitise_sample_rate(sample_rate)

    return mono_audio, sample_rate


def save_mono_audio(mono_audio, path, *, sample_rate):
    mono_audio = sanitise_mono_audio(mono_audio)
    path = sanitise_path(path)
    sample_rate = sanitise_sample_rate(sample_rate)

    soundfile.write(path, audio, sample_rate)

import librosa
import soundfile

from .sanitisation import sanitise_arg, sanitise_args


def load_audio(path, *, sample_rate=None, error_if_not_mono=True):
    path, error_if_not_mono = sanitise_args("path", "error_if_not_mono")

    if sample_rate is not None:
        sample_rate = sanitise_arg("sample_rate")

    audio, sample_rate = librosa.load(path, sr=sample_rate, mono=False)

    if error_if_not_mono and len(audio.shape) != 1:
        raise ValueError(f"audio at {path} is not mono")

    if len(audio) == 0:
        raise ValueError(f"audio at {path} is empty")

    return audio, sanitise_arg("sample_rate")


def save_audio(audio, path, *, sample_rate):
    _, path, sample_rate = sanitise_args("audio", "path", "sample_rate")
    soundfile.write(path, audio, samplerate=sample_rate, subtype="FLOAT")

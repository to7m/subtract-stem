from pathlib import Path
from fractions import Fraction

from subtract_stem_lib import *


project_dir = Path(
    "/home/to7m/Music/tmp jams or other things what i played in"
    "/2024-12-17_LizzieHedgjazzhogsRehearsalVideo"
)
raw_dir = project_dir / "raw_audio"
processed_dir = project_dir / "processed_audio"

print("loading keys audio")
keys_audio, sample_rate = load_audio(processed_dir / "keysMono.wav")
print("loading monitor audio")
monitor_audio, _ = load_audio(raw_dir / "monitor.wav")

keys_to_monitor_delay_s = find_delay_stem_s(
    stem_audio=keys_audio, mix_audio=monitor_audio,
    start_s=1, stop_s=-1,
    logger=logger
)
keys_to_monitor_eq_profile = GetEqProfile(
    stem_audio=keys_audio, mix_audio=monitor_audio,
    start_s=1, stop_s=-1, delay_stem_s=keys_to_monitor_delay_s,
    logger=logger
).run()
monitor_to_keys_eq_profile = safe_reciprocal(keys_to_monitor_eq_profile)

mic_paths = [
    raw_dir / "bass.wav",
    raw_dir / "kick.wav",
    raw_dir / "OH.wav",
    raw_dir / "snare.wav",
    raw_dir / "vox.wav"
]
for i in range(3):
    out_paths = [
        processed_dir / f"{mic_path.stem}_{i}.wav"
        for mic_path in mic_paths
    ]

    for mic_path, out_path in zip(mic_paths, out_paths):
        mic_audio = load_audio(mic_path)

        keys_mic_delay_s = find_delay_stem_s(
            stem_audio=keys_audio,
            mix_audio=mic_audio,
            start_s=1, stop_s=-1,
            logger=True
        )

        monitor_mic_delay = keys_mic_delay_s - keys_monitor_delay_s

        out_audio = subtract_intermediate_from_mix(
            stem_audio=keys_audio,
            intermediate_audio=monitor_audio,
            mix_audio=mic_audio,
            delay_stem_s=keys_mic_delay_s,
            delay_intermediate_s=monitor_mic_delay_s,
            intermediate_to_stem_eq_profile=monitor_to_keys_eq_profile
        )

        save_audio(out_path, out_audio, sample_rate)

class AudioToGrains:
    def __init__(
        self, *,
        mono_audio, sample_rate,
        start_s=Fraction(0), stop_s=None,
        delay_audio_s=Fraction(0),
        transform_len=TRANSFORM_LEN,
        additional_iterations_before=0, additional_iterations_after=0,
        num_of_retained=1,
        logger=None
    ):
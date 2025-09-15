import torch
import soundfile as sf
from pydub import AudioSegment, effects


class SileroTTSProcessor:
    """
    Wrapper for Silero TTS model with utilities for speech synthesis,
    normalization, speed adjustment, and optional reverb.
    """

    def __init__(self, speaker: str = "eugene", sample_rate: int = 48000):
        self.speaker = speaker
        self.sample_rate = sample_rate

        # load the Silero TTS model once
        self.model, _ = torch.hub.load(
            repo_or_dir="snakers4/silero-models",
            model="silero_tts",
            language="ru",
            speaker="v3_1_ru"
        )

    def synthesize(self, text: str) -> any:
        """
        Generate raw audio waveform (numpy array) from text.
        """
        audio = self.model.apply_tts(
            text=text,
            speaker=self.speaker,
            sample_rate=self.sample_rate,
            put_accent=True,
            put_yo=True,
        )
        return audio.numpy()

    def save_audio(self, audio, file_path: str):
        """
        Save audio waveform to WAV file.
        """
        sf.write(file_path, audio, self.sample_rate)
        print(f"Raw audio saved: {file_path}")

    def process_audio(self, in_file: str, out_file: str, speed: float = 0.9, reverb: bool = True):
        """
        Normalize loudness, adjust speed, and optionally add reverb.
        """
        sound = AudioSegment.from_wav(in_file)

        # normalize loudness
        sound = effects.normalize(sound)

        # adjust playback speed (tempo)
        sound = sound._spawn(sound.raw_data, overrides={
            "frame_rate": int(sound.frame_rate * speed)
        }).set_frame_rate(sound.frame_rate)

        # add light reverb (simulated with echo overlay)
        if reverb:
            delay = 120   # milliseconds
            decay = -20   # echo volume (dB)
            echo = sound.overlay(sound - abs(decay), position=delay)
            sound = echo

        sound.export(out_file, format="wav")
        print(f"Processed audio saved: {out_file} (speed={speed}, reverb={reverb})")


if __name__ == "__main__":
    text = """The legend of Romulus and Remus sets the tone for Rome's early history.
    Archaeological evidence reminds us the city emerged through the gradual coexistence of Latin settlements.
    Social and political institutions began to take shape here at the crossroads of trade and defense."""

    tts = SileroTTSProcessor(speaker="eugene")

    # synthesis
    audio = tts.synthesize(text)

    raw_file = "silero_out_raw.wav"
    final_file = "silero_out_final.wav"

    # save raw audio
    tts.save_audio(audio, raw_file)

    # normalize, change speed, add reverb
    tts.process_audio(raw_file, final_file, speed=0.9, reverb=True)

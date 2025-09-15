import torch
import soundfile as sf
from pydub import AudioSegment, effects


# load the model once
model, _ = torch.hub.load(
    repo_or_dir="snakers4/silero-models",
    model="silero_tts",
    language="ru",
    speaker="v3_1_ru"
)


def synthesize(text: str, speaker="eugene", sample_rate=48000):
    """
    Generate speech audio from text (no sentence splitting).
    """
    audio = model.apply_tts(
        text=text,
        speaker=speaker,
        sample_rate=sample_rate,
        put_accent=True,
        put_yo=True,
    )
    return audio.numpy()


def normalize_and_speed(in_file: str, out_file: str, speed: float = 0.9, reverb: bool = True):
    """
    Normalize volume, change playback speed (tempo), and optionally add light reverb.
    """
    sound = AudioSegment.from_wav(in_file)

    # normalize loudness
    sound = effects.normalize(sound)

    # change playback speed (tempo)
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
    print(f"File saved: {out_file} (speed={speed}, reverb={reverb})")


if __name__ == "__main__":
    text = """Легенда о Ромуле и Реме задаёт тон ранней истории Рима.
    Археологические данные напоминают, что город возник в ходе постепенного сосуществования латинских поселений.
    Социальные и политические институты начали формироваться здесь, на перекрёстке торговли и обороны. 
    Река Тибр стала главной торговой артерией и естественным рубежом для первых
        кварталов. Ранние поселения вокруг Палатина развивались через обмен, ремесла
        и совместные фортификационные решения. Скоро отношения между соседями закрепились
        в городское объединение."""

    audio = synthesize(text, speaker="eugene")

    raw_file = "silero_out_raw.wav"
    final_file = "silero_out_final.wav"
    sf.write(raw_file, audio, 48000)

    # normalization + slowdown + reverb
    normalize_and_speed(raw_file, final_file, speed=0.9, reverb=True)

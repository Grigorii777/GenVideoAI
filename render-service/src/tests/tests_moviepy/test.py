from pathlib import Path
from moviepy import ImageClip, AudioFileClip, CompositeVideoClip, concatenate_videoclips

FPS = 30
clips = []
root = Path(".")

def shot_num(p): return int(p.stem.split("-Sh")[-1])

for img in sorted(root.glob("Pr*-Ep*-Seq*.png")):
    base = img.stem  # Pr0-Ep0-Seq0
    for wav in sorted(root.glob(f"{base}-Sh*.wav"), key=shot_num):
        audio = AudioFileClip(str(wav))
        clip = (
            ImageClip(str(img))
            .with_duration(audio.duration)  # was set_duration
            .with_audio(audio)              # was set_audio
            .with_fps(FPS)                  # was set_fps
            .resized(height=1080)           # was resize
        )
        # Centre on a 1920x1080 canvas with a black background
        frame = CompositeVideoClip([clip.with_position("center")],
                                   size=(1920, 1080), bg_color=(0, 0, 0))
        clips.append(frame)

final = concatenate_videoclips(clips, method="chain")
final.write_videofile("output.mp4", fps=FPS, codec="libx264", audio_codec="aac")

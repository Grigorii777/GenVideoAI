import asyncio
import os

from scenarist.scenarist import ScenarioGenerator
from tts_processors.silero_tts_processor import SileroTTSProcessor


async def process_all(a):
    for ep in a.episodes:
        for seq in ep.sequences:
            print("Queued", seq.hierarchy_id)
            for sh in seq.shots:
                print("Shot", sh.hierarchy_id)

                tts = SileroTTSProcessor(speaker="eugene")

                # synthesis
                audio = tts.synthesize(sh.text)

                raw_file = f"{sh.hierarchy_id}_raw.wav"
                final_file = f"{sh.hierarchy_id}.wav"

                # save raw audio
                tts.save_audio(audio, raw_file)

                # normalize, change speed, add reverb
                tts.process_audio(raw_file, final_file, speed=0.87, reverb=True)

                os.remove(raw_file)


async def main():
    # Generate scenario
    s_gen = ScenarioGenerator()
    a = await s_gen.gen(
        "Roman Empire", "Documentary", 30, is_backup=True
    )
    # Generate images for all sequences
    await process_all(a)


if __name__ == "__main__":
    asyncio.run(main())
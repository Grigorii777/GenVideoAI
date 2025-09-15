import asyncio

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

                hierarchy_id = str(sh.hierarchy_id)

                # save raw audio to S3
                raw_key = await tts.save_audio(audio, hierarchy_id, variant="raw")

                # normalize, change speed, add reverb using the raw audio from S3
                final_key = await tts.process_audio(
                    None, hierarchy_id, speed=0.87, reverb=True
                )

                print("Raw key:", raw_key)
                print("Final key:", final_key)


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

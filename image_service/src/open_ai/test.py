import asyncio

from open_ai.image_generator import ImageGenerator
from saver.s3_saver import S3AsyncSaver
from scenarist.scenarist import ScenarioGenerator, get_json_scheme_example


async def generate_and_save(seq, img_gen: ImageGenerator, saver: S3AsyncSaver, prefix="media"):
    img = await img_gen.generate_image(seq.style.image + ". No Text", output_format="png")
    data = img if isinstance(img, bytes) else img[0]
    key = f"{prefix}/{seq.hierarchy_id}.png"
    await saver.save(data, key, content_type="image/png")
    return key

async def run_pipeline():
    s_gen = ScenarioGenerator()
    a = await s_gen.gen("Roman Empire", "Documentary", 30, schema=get_json_scheme_example(), is_backup=True)
    img_gen = ImageGenerator()
    async with S3AsyncSaver(bucket="GenVideoAI") as saver:
        tasks = []
        for ep in a.episodes:
            for seq in ep.sequences:
                print("Create task:", seq.hierarchy_id)
                tasks.append(asyncio.create_task(generate_and_save(seq, img_gen, saver)))

        # as ready
        for coro in asyncio.as_completed(tasks):
            saved_key = await coro
            print("Saved:", saved_key)

asyncio.run(run_pipeline())

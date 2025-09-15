import asyncio
from pathlib import Path
from typing import Union, List, Optional, Literal

from gpt_api.chatgpt_api import ChatGPTAPIAsync
from scenarist.scenarist import ScenarioGenerator, get_json_scheme_example


class ImageGenerator:
    async def generate_image(
        self,
        prompt: str,
        *,
        model: str = "gpt-image-1",
        size: Literal["1024x1024", "1024x1536", "1536x1024", "auto"] = "1024x1024",
        output_format: Literal["png", "jpeg", "webp"] = "png",
        quality: Optional[Literal["low", "medium", "high", "auto"]] = "low",
        background: Optional[Literal["transparent", "opaque", "auto"]] = None,
        output_compression: Optional[int] = None,  # range: 0–100
        n: int = 1,
        output_path: Optional[Union[str, Path]] = None,
    ) -> Union[bytes, List[bytes]]:
        """
        Asynchronously generate an image and optionally save it to disk.
        """
        role = """
        Create good quality images. You are creating images for videos.
        """
        api = ChatGPTAPIAsync(gpt_role=role, model=model, timeout=200)

        # just await the API call, no asyncio.run here
        result = await api.generate_image(
            prompt,
            size=size,
            output_format=output_format,
            quality=quality,
            background=background,
            output_compression=output_compression,
            n=n,
            output_path=output_path,
        )
        return result


async def process_all(a):
    tasks = []
    for ep in a.episodes:
        for seq in ep.sequences:
            print("Queued", seq.hierarchy_id)
            tasks.append(
                ImageGenerator().generate_image(
                    prompt=seq.style,
                    output_path=f"{seq.hierarchy_id}.png"
                )
            )

    results = await asyncio.gather(*tasks)
    print("All done:", results)


async def main():
    # Generate scenario
    s_gen = ScenarioGenerator()
    a = await s_gen.gen(
        "Roman Empire", "Documentary", 30,
        schema=get_json_scheme_example(),
        is_backup=True
    )

    # Generate images for all sequences
    await process_all(a)


if __name__ == "__main__":
    asyncio.run(main())

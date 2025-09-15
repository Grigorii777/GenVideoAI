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
        quality: Optional[Literal["low", "medium", "high", "auto"]] = "medium",
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

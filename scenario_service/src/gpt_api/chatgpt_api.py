import abc
import base64
from pathlib import Path
from typing import Optional, Literal, Union, List
from dotenv import load_dotenv
from openai import AsyncOpenAI
from openai.types.chat import (
    ChatCompletionSystemMessageParam,
    ChatCompletionUserMessageParam,
)

load_dotenv()


class GPTAPI(abc.ABC):
    """Abstract base class for GPT API clients."""

    @abc.abstractmethod
    async def ask(self, message: str, gpt_role: Optional[str] = None) -> str:
        """Send a message to the GPT model and return the response as text.

        Args:
            message: The user input message. Must be non-empty.
            gpt_role: Optional system role instruction that defines assistant behavior.

        Returns:
            The generated response from the model.

        Raises:
            ValueError: If ``message`` is empty.
        """
        ...


class ChatGPTAPIAsync(GPTAPI):
    """Asynchronous GPT API client using OpenAI's Chat Completions endpoint.

    This class provides an async method `ask` to send messages and
    receive responses from the GPT model.

    Attributes:
        model: The model identifier (e.g., ``gpt-5-nano``).
        gpt_role: Default system role instruction.
        timeout: Request timeout in seconds.
    """

    def __init__(self, model: str = "gpt-5-nano", gpt_role: Optional[str] = None, timeout: float = 60.0):
        """Initialize the async GPT API client.

        Args:
            model: Model identifier.
            gpt_role: Default system role instruction.
            timeout: Request timeout in seconds.
        """
        self.client = AsyncOpenAI()
        self.model = model
        self.gpt_role = gpt_role
        self.timeout = timeout

    async def ask(self, message: str, gpt_role: Optional[str] = None) -> str:
        """Send a message to the GPT model and return its response.

        Args:
            message: The user message to send.
            gpt_role: Optional system role instruction.

        Returns:
            The model's text response. Empty string if no content.

        Raises:
            ValueError: If ``message`` is empty.
        """
        if not message:
            raise ValueError("message must be non-empty")

        # Build messages list. System role should come first.
        messages = []
        role = gpt_role or self.gpt_role
        if role:
            messages.append(ChatCompletionSystemMessageParam(role="system", content=role))
        messages.append(ChatCompletionUserMessageParam(role="user", content=message))

        # Perform asynchronous request to OpenAI API
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            timeout=self.timeout,
        )

        # Extract and return response text
        return response.choices[0].message.content or ""

    async def generate_image(
        self,
        prompt: str,
        *,
        model: str = "gpt-image-1",
        size: Literal["1024x1024", "1024x1536", "1536x1024", "auto"] = "1024x1024",
        output_format: Literal["png", "jpeg", "webp"] = "png",
        quality: Optional[Literal["low", "medium", "high", "auto"]] = None,
        background: Optional[Literal["transparent", "opaque", "auto"]] = None,
        output_compression: Optional[int] = None,   # range: 0–100
        n: int = 1,
        output_path: Optional[Union[str, Path]] = None,
    ) -> Union[bytes, List[bytes]]:
        """
        Generate image(s) using the OpenAI Images API.

        Args:
            prompt: Text prompt describing the image to generate.
            model: Model identifier (default: "gpt-image-1").
            size: Image resolution (e.g., "1024x1024", "1536x1024").
            output_format: Output format ("png", "jpeg", or "webp").
            quality: Optional quality level ("low", "medium", "high", "auto").
            background: Optional background setting ("transparent", "opaque", "auto").
            output_compression: Optional compression level for JPEG/WEBP (0–100).
            n: Number of images to generate (default: 1).
            output_path: Path for saving output. If n > 1, treated as a folder.

        Returns:
            - Bytes of a single image if n == 1.
            - List of image bytes if n > 1.

        Raises:
            ValueError: If prompt is empty or n < 1.

        Notes:
            - To generate images with transparent background, set
              background="transparent" and output_format="png" or "webp".
            - Images are returned as base64-encoded strings by the API.
        """
        if not prompt:
            raise ValueError("prompt must be non-empty")
        if n < 1:
            raise ValueError("n must be >= 1")

        kwargs = {
            "model": model,
            "prompt": prompt,
            "size": size,
            "output_format": output_format,
            "n": n,
        }
        if quality is not None:
            kwargs["quality"] = quality
        if background is not None:
            kwargs["background"] = background
        if output_compression is not None:
            kwargs["output_compression"] = int(output_compression)

        # Perform async request to OpenAI Images API
        resp = await self.client.images.generate(
            **kwargs,
            timeout=self.timeout,
        )

        # Decode base64 JSON to raw image bytes
        imgs: List[bytes] = [base64.b64decode(d.b64_json) for d in resp.data]

        # Optionally save to disk
        if output_path:
            output_path = Path(output_path)
            ext = {"png": ".png", "jpeg": ".jpg", "webp": ".webp"}[output_format]
            if n == 1:
                p = output_path if output_path.suffix else output_path.with_suffix(ext)
                p.parent.mkdir(parents=True, exist_ok=True)
                p.write_bytes(imgs[0])
            else:
                output_path.mkdir(parents=True, exist_ok=True)
                for i, b in enumerate(imgs, 1):
                    (output_path / f"image_{i}{ext}").write_bytes(b)

        return imgs[0] if n == 1 else imgs

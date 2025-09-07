import abc
from typing import Optional
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
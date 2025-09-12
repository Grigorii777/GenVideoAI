from typing import Optional

import pytest

from gpt_api.chatgpt_api import ChatGPTAPIAsync


# @pytest.mark.skip("Skip the test because you have to pay)")
class TestChatGPT:
    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        ("message","expected"),
        [("Send only letter A", "A")]
    )
    async def test_ask(self, message: str, expected: Optional[str]):
        api = ChatGPTAPIAsync()
        assert await api.ask(message) == expected

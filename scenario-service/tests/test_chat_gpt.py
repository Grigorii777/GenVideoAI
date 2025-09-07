from typing import Optional
from gpt_api.chatgpt_api import ChatGPTAPI


import pytest

@pytest.mark.skip("Skip the test because you have to pay)")
class TestChatGPT:
    @pytest.mark.parametrize(
        ("message","expected"),
        [("Send only letter A", "A")]
    )
    def test_ask(self, message: str, expected: Optional[str]):
        api = ChatGPTAPI()
        assert api.ask(message) == expected

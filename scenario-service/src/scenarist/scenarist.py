from pydantic import BaseModel, Field


class Scenarist:
    def __init__(self):
        self.info = ""

    def gen_scenario(self, ):
        api = ChatGPTAPI()
        api.ask(self.info)

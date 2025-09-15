import asyncio
import json
from pathlib import Path
from pprint import pprint
from typing import Any
from uuid import uuid4
from copy import copy

import yaml

from gpt_api.chatgpt_api import ChatGPTAPIAsync
from entities.entities import ProjectEntity


def deep_exclude_key(obj: Any, key: str) -> Any:
    if isinstance(obj, dict):
        return {k: deep_exclude_key(v, key) for k, v in obj.items() if k != key}
    if isinstance(obj, list):
        return [deep_exclude_key(v, key) for v in obj]
    return obj

def get_json_scheme_example():
    data_base = ProjectEntity.example().model_dump()
    data = deep_exclude_key(data_base, "id")
    json_scenario_schema = deep_exclude_key(data, "hierarchy_id")
    return json_scenario_schema


class ScenarioGenerator:
    entities = ["episodes", "sequences", "shots"]

    async def _gen(self, theme: str, style: str, duration: int, lang="ru", schema: dict = None):
        role = f"""
                You are a scriptwriter for educational and entertainment videos. 
                Strictly adhere to the JSON response schema.
                Requirements:
                1) Return ONLY valid JSON without explanations and Markdown.
                2) Maintain the hierarchy:  project -> episodes -> sequences -> shots
                    In each project there are episodes; 
                    in each episode there are 3–7 sequences; 
                    in each sequence there are 5–10 shots; 
                    in each shot there are 3–5 text sentences.
                3) Do not add fields outside the schema.
                4) All language: en. Shot text language: {lang}.
                Scheme:
                    {str(schema)}
                """
        api = ChatGPTAPIAsync(gpt_role=role, timeout=200)
        prompt = f"""
                Topic: {theme}
                Style/reference: {style}
                Create text in shots for {duration} seconds of aloud reading 
                """
        res = await api.ask(prompt)
        return res

    def _update_dict_fields(self, data: dict, path: dict | None = None, id_factory=uuid4) -> None:
        """
        Mutates `data`:
          - sets data["id"] = id_factory()
          - sets data["hierarchy_id"] = copy of the current path (project/episode/sequence/shot)
          - recursively traverses one found child type from l and adds the path to the index
        """
        if path is None:
            path = {"project": 0}  # root

        data["id"] = id_factory()
        data["hierarchy_id"] = copy(path)

        # looking for what type of children this node has
        for child_key in self.entities:
            children = data.get(child_key)
            if isinstance(children, list):
                singular = child_key[:-1]  # episodes->episode, sequences->sequence, shots->shot
                for idx, child in enumerate(children):
                    next_path = copy(path)
                    next_path[singular] = idx
                    self._update_dict_fields(child, next_path, id_factory)
                break  # A node can only have one type of children.

    async def gen(self, theme: str, style: str, duration: int, lang="ru", schema: dict = None, is_backup: bool = False, file_path: str = "ans.yaml"):
        if not is_backup:
            ans = await self._gen(theme, style, duration, schema=schema, lang=lang)
            data = json.loads(ans)
            self._update_dict_fields(data)
        else:
            data = yaml.safe_load(Path(file_path).read_text(encoding="utf-8"))

        model_data = ProjectEntity.model_validate(data)
        return model_data

    async def gen_to_file(self, theme: str, style: str, duration: int, lang="ru", schema: dict = None, file_path: str = "ans.yaml"):
        ans = await self.gen(theme, style, duration, schema=schema, lang=lang)

        data = ans.model_dump(mode="json")
        with open(file_path, "w", encoding="utf-8") as f:
            yaml.safe_dump(data, f, allow_unicode=True, sort_keys=False)


# s_gen = ScenarioGenerator()
# asyncio.run(s_gen.gen_to_file("Roman Empire", "Documentary", 600, schema=get_json_scheme_example()))
# a = asyncio.run(s_gen.gen("Roman Empire", "Documentary", 30, schema=get_json_scheme_example(),
#                           is_backup=True))
# pprint(a.model_dump(mode="json"))


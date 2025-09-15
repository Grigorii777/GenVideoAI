import asyncio
from pprint import pprint

from scenarist.scenarist import ScenarioGenerator, get_json_scheme_example

s_gen = ScenarioGenerator()
a = asyncio.run(s_gen.gen("Roman Empire", "Documentary", 30, schema=get_json_scheme_example(), is_backup=True))
pprint(a.model_dump())


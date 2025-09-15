import asyncio
from typing import Any

from open_ai.image_generator import ImageGenerator
from saver.s3_saver import S3AsyncSaver
from scenarist.scenarist import ScenarioGenerator, get_json_scheme_example


def _extract_hierarchy_id(entity: Any) -> str:
    """Return hierarchy id for ``entity``.

    Accepts either a string hierarchy id or a model instance exposing
    ``hierarchy_id`` attribute.  Raises ``AttributeError`` when the hierarchy id
    cannot be resolved – this helps us fail fast if a wrong object is passed.
    """

    if isinstance(entity, str):
        return entity

    if hasattr(entity, "hierarchy_id"):
        return str(getattr(entity, "hierarchy_id"))

    raise AttributeError("Entity must be a hierarchy id string or expose hierarchy_id attribute")


def _build_entity_prefix(hierarchy_id, *prefix_parts: str) -> str:
    """Build an S3 key prefix based on hierarchy id.

    The hierarchy id comes in a form like ``Pr0-Ep0-Seq0``. For easier browsing in
    object storage we convert it to a path-like string ``Pr0/Ep0/Seq0``.  Optional
    prefix parts (e.g. ``"media"``) can be provided to nest the hierarchy under a
    custom root.
    """

    entity_path = str(hierarchy_id).replace("-", "/")
    cleaned_parts = [part.strip("/") for part in prefix_parts if part]
    return "/".join(cleaned_parts + [entity_path]) if cleaned_parts else entity_path


def build_entity_asset_path(entity: Any, prefix: str | None = None, extension: str = "png") -> str:
    """Construct an asset storage path based on entity hierarchy."""

    hierarchy_id = _extract_hierarchy_id(entity)
    key_prefix = _build_entity_prefix(hierarchy_id, prefix)
    ext = extension.lstrip(".")
    return f"{key_prefix}/{hierarchy_id}.{ext}"


async def generate_and_save(
    seq,
    img_gen: ImageGenerator,
    saver: S3AsyncSaver,
    prefix: str | None = None,
    *,
    model: str | None = None,
):
    generation_kwargs = {"output_format": "png"}
    if model is not None:
        generation_kwargs["model"] = model

    img = await img_gen.generate_image(seq.style.image + ". No Text", **generation_kwargs)
    data = img if isinstance(img, bytes) else img[0]
    key = build_entity_asset_path(seq, prefix=prefix)
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

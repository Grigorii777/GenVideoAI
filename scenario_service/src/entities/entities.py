from pathlib import Path

import yaml
from uuid import UUID
from scenario_dto.dto import (
    ProjectDTO,
    EpisodeDTO,
    SequenceDTO,
    ShotDTO,
    ShotStyle,
    SequenceStyle,
    ProjectId,
    EpisodeId,
    SequenceId,
    ShotId,
)

BASE_DIR = Path(__file__).resolve().parent
STYLES_PATH = BASE_DIR / "styles.yml"


def load_styles(path: Path = STYLES_PATH) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

STYLES = load_styles()


class ShotEntity(ShotDTO):
    @classmethod
    def example(cls) -> "ShotEntity":
        data = STYLES["ShotEntity"]
        return cls(
            id=UUID(int=0),
            title=data["title"],
            style=ShotStyle(**data["style"]),
            text="Shot text",
            hierarchy_id=ShotId(project=0, episode=0, sequence=0, shot=0),
        )


class SequenceEntity(SequenceDTO):
    @classmethod
    def example(cls) -> "SequenceEntity":
        data = STYLES["SequenceEntity"]
        return cls(
            id=UUID(int=0),
            title=data["title"],
            style=SequenceStyle(**data["style"]),
            hierarchy_id=SequenceId(project=0, episode=0, sequence=0),
            shots=[ShotEntity.example()],
        )


class EpisodeEntity(EpisodeDTO):
    @classmethod
    def example(cls) -> "EpisodeEntity":
        data = STYLES["EpisodeEntity"]
        return cls(
            id=UUID(int=0),
            title=data["title"],
            style=data["style"],
            hierarchy_id=EpisodeId(project=0, episode=0),
            sequences=[SequenceEntity.example()],
        )


class ProjectEntity(ProjectDTO):
    @classmethod
    def example(cls) -> "ProjectEntity":
        data = STYLES["ProjectEntity"]
        return cls(
            id=UUID(int=0),
            title=data["title"],
            style=data["style"],
            hierarchy_id=ProjectId(project=0),
            episodes=[EpisodeEntity.example()],
        )


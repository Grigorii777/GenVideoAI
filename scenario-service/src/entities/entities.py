import json
from pprint import pprint
from typing import Any
from uuid import UUID
from scenario_dto.dto import (
    ProjectDTO, EpisodeDTO, SequenceDTO, ShotDTO,
    ProjectId, EpisodeId, SequenceId, ShotId,
)


class ShotEntity(ShotDTO):
    @classmethod
    def example(cls) -> "ShotEntity":
        return cls(
            id=UUID(int=0),
            title="Shot title",
            style="Shot style",
            text="Shot text",
            hierarchy_id=ShotId(project=0, episode=0, sequence=0, shot=0),
        )


class SequenceEntity(SequenceDTO):
    @classmethod
    def example(cls) -> "SequenceEntity":
        return cls(
            id=UUID(int=0),
            title="Sequence title",
            style="Sequence style",
            hierarchy_id=SequenceId(project=0, episode=0, sequence=0),
            shots=[ShotEntity.example(), ShotEntity.example()],
        )


class EpisodeEntity(EpisodeDTO):
    @classmethod
    def example(cls) -> "EpisodeEntity":
        return cls(
            id=UUID(int=0),
            title="Episode title",
            style="Episode style",
            hierarchy_id=EpisodeId(project=0, episode=0),
            sequences=[SequenceEntity.example(), SequenceEntity.example()],
        )


class ProjectEntity(ProjectDTO):
    @classmethod
    def example(cls) -> "ProjectEntity":
        return cls(
            id=UUID(int=0),
            title="Project name",
            style="Project style",
            hierarchy_id=ProjectId(project=0),
            episodes=[EpisodeEntity.example(), EpisodeEntity.example()],
        )


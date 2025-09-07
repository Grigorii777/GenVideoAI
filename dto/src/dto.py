from __future__ import annotations
import abc, re
from typing import ClassVar, Pattern, List, NoReturn
from pydantic import BaseModel, Field, field_validator
from uuid import UUID


class HierarchyId(abc.ABC, BaseModel):
    pattern_str: ClassVar[str] = ""
    segment: ClassVar[str] = ""
    sep: ClassVar[str] = "-"
    regexp: ClassVar[Pattern[str]]

    def __init_subclass__(cls, **kw):
        super().__init_subclass__(**kw)
        base = getattr(super(cls, cls), "pattern_str", "")
        seg = getattr(cls, "segment", "")
        cls.pattern_str = seg if not base else (base + (cls.sep + seg if seg else ""))
        cls.regexp = re.compile(rf"^{cls.pattern_str}$")

    def __str__(self) -> str:
        return ""

    @classmethod
    @abc.abstractmethod
    def from_str(cls, s: str) -> HierarchyId: ...

    @classmethod
    def _err(cls, value: str) -> NoReturn:
        try:
            expected = cls.regexp.pattern
        except Exception: # pylint: disable=broad-except
            expected = "|".join(
                t.regexp.pattern for t in (ProjectId, EpisodeId, SequenceId, ShotId)
            )
        raise ValueError(f"Invalid {cls.__name__}: expected '{expected}', got '{value}'")

    @classmethod
    def parse(cls, s: str) -> HierarchyId | ValueError:
        for t in (ShotId, SequenceId, EpisodeId, ProjectId):
            if t.regexp.fullmatch(s):
                return t.from_str(s)
        raise cls._err(s)


class ProjectId(HierarchyId):
    segment = r"Pr(\d+)"
    project: int = Field(ge=0)

    @classmethod
    def from_str(cls, s: str) -> ProjectId:
        m = cls.regexp.fullmatch(s)
        if not m: raise cls._err(s)
        return cls(project=int(m.group(1)))

    def __str__(self) -> str:
        return f"Pr{self.project}"


class EpisodeId(HierarchyId):
    segment = r"Ep(\d+)"
    episode: int = Field(ge=0)

    @classmethod
    def from_str(cls, s: str) -> EpisodeId:
        m = cls.regexp.fullmatch(s)
        if not m: raise cls._err(s)
        return cls(episode=int(m.group(1)))

    def __str__(self) -> str:
        return f"Ep{self.episode}"


class SequenceId(EpisodeId):
    segment = r"Seq(\d+)"
    sequence: int = Field(ge=0)

    @classmethod
    def from_str(cls, s: str) -> SequenceId:
        m = cls.regexp.fullmatch(s)
        if not m: raise cls._err(s)
        return cls(episode=int(m.group(1)), sequence=int(m.group(2)))

    def __str__(self) -> str:
        return f"{super().__str__()}-Seq{self.sequence}"

    def parent(self) -> EpisodeId:
        return EpisodeId(episode=self.episode)


class ShotId(SequenceId):
    segment = r"Sh(\d+)"
    shot: int = Field(ge=0)

    @classmethod
    def from_str(cls, s: str) -> ShotId:
        m = cls.regexp.fullmatch(s)
        if not m: raise cls._err(s)
        return cls(episode=int(m.group(1)), sequence=int(m.group(2)), shot=int(m.group(3)))

    def __str__(self) -> str:
        return f"{super().__str__()}-Sh{self.shot}"

    def parent(self) -> SequenceId:
        return SequenceId(episode=self.episode, sequence=self.sequence)


class Storyboard(abc.ABC, BaseModel):
    id: UUID
    title: str
    style: str
    hierarchy_id: HierarchyId

    @field_validator("hierarchy_id", mode="before")
    @classmethod
    def _coerce_hid(cls, v):
        target = cls.model_fields["hierarchy_id"].annotation
        if type(v) is target:
            return v
        if isinstance(v, HierarchyId):
            raise TypeError(f"Expected {target.__name__}, got {type(v).__name__}")
        if isinstance(v, str):
            return target.from_str(v.strip())
        raise TypeError(f"hierarchy_id must be {target.__name__} | str")


class ShotDTO(Storyboard):
    text: str
    hierarchy_id: ShotId


class SequenceDTO(Storyboard):
    shots: List[ShotDTO]
    hierarchy_id: SequenceId


class EpisodeDTO(Storyboard):
    sequences: List[SequenceDTO]
    hierarchy_id: EpisodeId


class ProjectDTO(BaseModel):
    episodes: List[EpisodeDTO]
    hierarchy_id: ProjectId

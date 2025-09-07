from __future__ import annotations
import abc, re
from functools import lru_cache
from typing import ClassVar, Pattern, List, NoReturn
from pydantic import BaseModel, Field, field_validator
from uuid import UUID


class HierarchyId(abc.ABC, BaseModel):
    _pattern_str: ClassVar[str] = ""
    _sep: ClassVar[str] = "-"
    _regexp: ClassVar[Pattern[str]]
    model_config = {"extra": "forbid"}
    _all_children: ClassVar[list[type[HierarchyId]]] = []

    def __init_subclass__(cls, **kw):
        super().__init_subclass__(**kw)
        base = getattr(super(cls, cls), "_pattern_str", "")
        seg = cls._segment()
        cls._pattern_str = seg if not base else (base + (cls._sep + seg if seg else ""))
        cls._regexp = re.compile(rf"^{cls._pattern_str}$")

    @classmethod
    @abc.abstractmethod
    def _segment(cls) -> str:
        return ""

    @abc.abstractmethod
    def __str__(self) -> str:
        return ""

    @classmethod
    def all_descendants(cls):
        res = []
        for sub in cls.__subclasses__():
            res.append(sub)
            res.extend(sub.all_descendants())
        return res

    @classmethod
    @abc.abstractmethod
    def from_str(cls, s: str) -> HierarchyId: ...

    @classmethod
    def _err(cls, value: str) -> NoReturn:
        try:
            expected = cls._regexp.pattern
        except Exception: # pylint: disable=broad-except
            expected = "|".join(
                t._regexp.pattern for t in cls._all_children
            )
        raise ValueError(f"Invalid {cls.__name__}: expected '{expected}', got '{value}'")

    @classmethod
    def parse(cls, s: str) -> HierarchyId | ValueError:
        for t in cls._all_children:
            if t._regexp.fullmatch(s):
                return t.from_str(s)
        cls._err(s)


class ProjectId(HierarchyId):
    project: int = Field(ge=0)

    @classmethod
    def _segment(cls) -> str:
        return r"Pr(\d+)"


    @classmethod
    def from_str(cls, s: str) -> ProjectId:
        m = cls._regexp.fullmatch(s)
        if not m: cls._err(s)
        return cls(project=int(m.group(1)))

    def __str__(self) -> str:
        return f"Pr{self.project}"


class EpisodeId(ProjectId):
    episode: int = Field(ge=0)

    @classmethod
    def _segment(cls) -> str:
        return r"Ep(\d+)"

    @classmethod
    def from_str(cls, s: str) -> "EpisodeId":
        m = cls._regexp.fullmatch(s)
        if not m: cls._err(s)
        return cls(project=int(m.group(1)), episode=int(m.group(2)))

    def __str__(self) -> str:
        return f"{super().__str__()}-Ep{self.episode}"

    def parent(self) -> ProjectId:
        return ProjectId(project=self.project)


class SequenceId(EpisodeId):
    sequence: int = Field(ge=0)

    @classmethod
    def _segment(cls) -> str:
        return r"Seq(\d+)"

    @classmethod
    def from_str(cls, s: str) -> "SequenceId":
        m = cls._regexp.fullmatch(s)
        if not m: cls._err(s)
        return cls(project=int(m.group(1)), episode=int(m.group(2)), sequence=int(m.group(3)))

    def __str__(self) -> str:
        return f"{super().__str__()}-Seq{self.sequence}"

    def parent(self) -> EpisodeId:
        return EpisodeId(project=self.project, episode=self.episode)


class ShotId(SequenceId):
    shot: int = Field(ge=0)

    @classmethod
    def _segment(cls) -> str:
        return r"Sh(\d+)"

    @classmethod
    def from_str(cls, s: str) -> "ShotId":
        m = cls._regexp.fullmatch(s)
        if not m: cls._err(s)
        return cls(
            project=int(m.group(1)),
            episode=int(m.group(2)),
            sequence=int(m.group(3)),
            shot=int(m.group(4)),
        )

    def __str__(self) -> str:
        return f"{super().__str__()}-Sh{self.shot}"

    def parent(self) -> SequenceId:
        return SequenceId(project=self.project, episode=self.episode, sequence=self.sequence)


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
            raise ValueError(f"Expected {target.__name__}, got {type(v).__name__}")
        if isinstance(v, str):
            return target.from_str(v.strip())
        if isinstance(v, dict):
            return target(**v)
        raise ValueError(f"hierarchy_id must be {target.__name__} | str | dict")


class ShotDTO(Storyboard):
    text: str
    hierarchy_id: ShotId


class SequenceDTO(Storyboard):
    shots: List[ShotDTO]
    hierarchy_id: SequenceId


class EpisodeDTO(Storyboard):
    sequences: List[SequenceDTO]
    hierarchy_id: EpisodeId


class ProjectDTO(Storyboard):
    episodes: List[EpisodeDTO]
    hierarchy_id: ProjectId


HierarchyId._all_children = HierarchyId.all_descendants()

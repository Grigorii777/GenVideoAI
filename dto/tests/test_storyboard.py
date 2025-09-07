# tests/test_storyboard.py
import pytest
from uuid import UUID
from pydantic import ValidationError

from scenario_dto.dto import (
    HierarchyId,
    ProjectId,
    EpisodeId,
    SequenceId,
    ShotId,
    ProjectDTO,
    EpisodeDTO,
    SequenceDTO,
    ShotDTO,
)


# ---------- ProjectId ---------------------------------------------------------
class TestProjectId:
    @pytest.mark.parametrize("s,n", [
        ("Pr0", 0),
        ("Pr1", 1),
        ("Pr123", 123),
    ])
    def test_from_str_ok(self, s, n):
        # Should parse valid strings and preserve numeric value
        pid = ProjectId.from_str(s)
        assert isinstance(pid, ProjectId)
        assert pid.project == n
        assert str(pid) == s

    @pytest.mark.parametrize("s", ["", "Pr", "Pr-1", "PrA", "Ep1", "Pr1-Ep2"])
    def test_from_str_err(self, s):
        # Invalid formats must raise ValueError
        with pytest.raises(ValueError):
            ProjectId.from_str(s)


# ---------- EpisodeId ---------------------------------------------------------
class TestEpisodeId:
    @pytest.mark.parametrize("s,pr,ep", [
        ("Pr0-Ep0", 0, 0),
        ("Pr1-Ep2", 1, 2),
        ("Pr10-Ep25", 10, 25),
    ])
    def test_from_str_ok(self, s, pr, ep):
        obj = EpisodeId.from_str(s)
        assert isinstance(obj, EpisodeId)
        assert (obj.project, obj.episode) == (pr, ep)
        assert str(obj) == s

    @pytest.mark.parametrize("s", [
        "Ep1", "Pr1", "Pr1-Ep", "Pr-Ep1", "Pr1-EpA", "Pr1-Ep1-Seq2", ""
    ])
    def test_from_str_err(self, s):
        with pytest.raises(ValueError):
            EpisodeId.from_str(s)

    def test_parent(self):
        # Requires EpisodeId.parent() -> ProjectId to be implemented
        ep = EpisodeId.from_str("Pr3-Ep7")
        parent = ep.parent()
        assert isinstance(parent, ProjectId)
        assert str(parent) == "Pr3"


# ---------- SequenceId --------------------------------------------------------
class TestSequenceId:
    @pytest.mark.parametrize("s,pr,ep,seq", [
        ("Pr0-Ep0-Seq0", 0, 0, 0),
        ("Pr1-Ep2-Seq3", 1, 2, 3),
        ("Pr10-Ep25-Seq99", 10, 25, 99),
    ])
    def test_from_str_ok(self, s, pr, ep, seq):
        obj = SequenceId.from_str(s)
        assert isinstance(obj, SequenceId)
        assert (obj.project, obj.episode, obj.sequence) == (pr, ep, seq)
        assert str(obj) == s

    @pytest.mark.parametrize("s", [
        "Pr1", "Pr1-Ep2", "Pr1-Ep2-Seq", "Pr-Ep2-Seq3", "Pr1-EpA-Seq3", ""
    ])
    def test_from_str_err(self, s):
        with pytest.raises(ValueError):
            SequenceId.from_str(s)


# ---------- ShotId ------------------------------------------------------------
class TestShotId:
    @pytest.mark.parametrize("s,pr,ep,seq,sh", [
        ("Pr0-Ep0-Seq0-Sh0", 0, 0, 0, 0),
        ("Pr1-Ep2-Seq3-Sh4", 1, 2, 3, 4),
        ("Pr10-Ep25-Seq99-Sh123", 10, 25, 99, 123),
    ])
    def test_from_str_ok(self, s, pr, ep, seq, sh):
        obj = ShotId.from_str(s)
        assert isinstance(obj, ShotId)
        assert (obj.project, obj.episode, obj.sequence, obj.shot) == (pr, ep, seq, sh)
        assert str(obj) == s

    @pytest.mark.parametrize("s", [
        "Pr1", "Pr1-Ep2", "Pr1-Ep2-Seq3", "Pr1-Ep2-Seq3-Sh",
        "Pr1-EpA-Seq3-Sh4", "Pr-Ep2-Seq3-Sh4", ""
    ])
    def test_from_str_err(self, s):
        with pytest.raises(ValueError):
            ShotId.from_str(s)

    def test_parent(self):
        sh = ShotId.from_str("Pr2-Ep4-Seq6-Sh8")
        parent = sh.parent()
        assert isinstance(parent, SequenceId)
        assert str(parent) == "Pr2-Ep4-Seq6"


# ---------- Factory parse() ---------------------------------------------------
class TestHierarchyParse:
    @pytest.mark.parametrize("s,cls_", [
        ("Pr5", ProjectId),
        ("Pr5-Ep1", EpisodeId),
        ("Pr5-Ep1-Seq9", SequenceId),
        ("Pr5-Ep1-Seq9-Sh3", ShotId),
    ])
    def test_parse_ok(self, s, cls_):
        obj = HierarchyId.parse(s)
        assert isinstance(obj, cls_)
        assert str(obj) == s

    @pytest.mark.parametrize("s", ["Epx", "Seq1", "Sh1", "Ep1-Seq", "random", ""])
    def test_parse_err(self, s):
        with pytest.raises(ValueError):
            HierarchyId.parse(s)


# ---------- Storyboard validator (strict) -------------------------------------
class TestStoryboardValidator:
    def test_shotdto_accepts_exact_type(self):
        dto = ShotDTO(
            id=UUID(int=1),
            title="t",
            style="s",
            text="x",
            hierarchy_id=ShotId.from_str("Pr1-Ep2-Seq3-Sh4"),
        )
        assert isinstance(dto.hierarchy_id, ShotId)

    def test_shotdto_rejects_other_hierarchy_types(self):
        with pytest.raises(ValidationError, match="Expected ShotId, got SequenceId"):
            ShotDTO(
                id=UUID(int=2), title="t", style="s", text="x",
                hierarchy_id=SequenceId.from_str("Pr1-Ep2-Seq3"),  # type: ignore[arg-type]
            )
        with pytest.raises(ValidationError, match="Expected ShotId, got EpisodeId"):
            ShotDTO(
                id=UUID(int=3), title="t", style="s", text="x",
                hierarchy_id=EpisodeId.from_str("Pr1-Ep2"),  # type: ignore[arg-type]
            )

    @pytest.mark.parametrize("s", [
        "Pr0-Ep0-Seq0-Sh0",
        "Pr1-Ep2-Seq3-Sh4",
        "Pr10-Ep25-Seq99-Sh123",
    ])
    def test_shotdto_accepts_string_and_parses(self, s):
        dto = ShotDTO(
            id=UUID(int=4),
            title="t",
            style="s",
            text="x",
            hierarchy_id=s,  # type: ignore[arg-type]
        )
        assert isinstance(dto.hierarchy_id, ShotId)
        assert str(dto.hierarchy_id) == s

    def test_sequencedto_and_episodedto_strictness(self):
        with pytest.raises(ValidationError, match="Expected SequenceId, got ShotId"):
            SequenceDTO(
                id=UUID(int=7), title="bad", style="x", shots=[],
                hierarchy_id=ShotId.from_str("Pr1-Ep1-Seq1-Sh1"),
            )

        with pytest.raises(ValidationError, match="Expected EpisodeId, got SequenceId"):
            EpisodeDTO(
                id=UUID(int=8), title="bad", style="x", sequences=[],
                hierarchy_id=SequenceId.from_str("Pr1-Ep1-Seq1"),  # type: ignore[arg-type]
            )


# ---------- Using mocker to assert from_str is called -------------------------
class TestValidatorWithMocker:
    def test_shotdto_calls_from_str_for_string(self, mocker):
        spy = mocker.spy(ShotId, "from_str")
        s = "Pr3-Ep4-Seq5-Sh6"
        dto = ShotDTO(
            id=UUID(int=9),
            title="t",
            style="s",
            text="x",
            hierarchy_id=s,  # type: ignore[arg-type]
        )
        assert isinstance(dto.hierarchy_id, ShotId)
        spy.assert_called_once_with(s)

    def test_episodedto_calls_from_str_for_string(self, mocker):
        spy = mocker.spy(EpisodeId, "from_str")
        s = "Pr42-Ep1"
        dto = EpisodeDTO(
            id=UUID(int=10),
            title="t",
            style="s",
            sequences=[],
            hierarchy_id=s,  # type: ignore[arg-type]
        )
        assert isinstance(dto.hierarchy_id, EpisodeId)
        spy.assert_called_once_with(s)


# ---------- ProjectDTO --------------------------------------------------------
class TestProjectDTO:
    def test_accepts_projectid_instance(self):
        dto = ProjectDTO(id=UUID(int=201), title="p", style="s",
                         episodes=[], hierarchy_id=ProjectId.from_str("Pr2"))
        assert isinstance(dto.hierarchy_id, ProjectId)

    def test_accepts_projectid_dict(self):
        dto = ProjectDTO(id=UUID(int=202), title="p", style="s",
                         episodes=[], hierarchy_id={"project": 3})
        assert dto.hierarchy_id.project == 3

    def test_accepts_string(self):
        dto = ProjectDTO(id=UUID(int=203), title="p", style="s",
                         episodes=[], hierarchy_id="Pr4")
        assert str(dto.hierarchy_id) == "Pr4"

    @pytest.mark.parametrize("wrong", [EpisodeId.from_str("Pr1-Ep1"),
                                       SequenceId.from_str("Pr1-Ep1-Seq2"),
                                       ShotId.from_str("Pr1-Ep1-Seq2-Sh3")])
    def test_rejects_other_id_models(self, wrong):
        with pytest.raises(ValueError):
            ProjectDTO(id=UUID(int=204), title="p", style="s",
                       episodes=[], hierarchy_id=wrong)

    def test_dump_shape(self):
        dto = ProjectDTO(id=UUID(int=205), title="p", style="s",
                         episodes=[], hierarchy_id=ProjectId.from_str("Pr9"))
        assert dto.model_dump()["hierarchy_id"] == {"project": 9}


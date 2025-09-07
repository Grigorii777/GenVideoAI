# tests/test_storyboard_hierarchy.py
import pytest
from uuid import UUID

from pydantic import ValidationError

from dto.src.dto import (
    HierarchyId,
    EpisodeId,
    SequenceId,
    ShotId,
    EpisodeDTO,
    SequenceDTO,
    ShotDTO, ProjectId, ProjectDTO,
)

# ---------- EpisodeId ---------------------------------------------------------
class TestEpisodeId:
    @pytest.mark.parametrize("s,ep", [
        ("Ep0", 0),
        ("Ep1", 1),
        ("Ep123", 123),
    ])
    def test_from_str_ok(self, s, ep):
        obj = EpisodeId.from_str(s)
        assert isinstance(obj, EpisodeId)
        assert obj.episode == ep
        assert str(obj) == s  # __str__ via super()

    @pytest.mark.parametrize("s", [
        "Ep", "Ep-1", "EpA", "Seq1", "Ep1-Seq2", "Ep1-Seq2-Sh3", "1", "", " Ep1 ",
    ])
    def test_from_str_err(self, s):
        with pytest.raises(ValueError) as e:
            EpisodeId.from_str(s)
        assert "Invalid EpisodeId" in str(e.value)

# ---------- SequenceId --------------------------------------------------------
class TestSequenceId:
    @pytest.mark.parametrize("s,ep,seq", [
        ("Ep0-Seq0", 0, 0),
        ("Ep1-Seq2", 1, 2),
        ("Ep10-Seq25", 10, 25),
    ])
    def test_from_str_ok(self, s, ep, seq):
        obj = SequenceId.from_str(s)
        assert isinstance(obj, SequenceId)
        assert obj.episode == ep and obj.sequence == seq
        assert str(obj) == s  # __str__ via super() chain

    @pytest.mark.parametrize("s", [
        "Ep1", "Seq2", "Ep1-Seq", "Ep-Seq2", "Ep1-Seq2-Sh3", "Ep1-SeqA", ""
    ])
    def test_from_str_err(self, s):
        with pytest.raises(ValueError) as e:
            SequenceId.from_str(s)
        assert "Invalid SequenceId" in str(e.value)

    def test_parent(self):
        sid = SequenceId.from_str("Ep3-Seq7")
        parent = sid.parent()
        assert isinstance(parent, EpisodeId)
        assert str(parent) == "Ep3"

# ---------- ShotId ------------------------------------------------------------
class TestShotId:
    @pytest.mark.parametrize("s,ep,seq,sh", [
        ("Ep0-Seq0-Sh0", 0, 0, 0),
        ("Ep1-Seq2-Sh3", 1, 2, 3),
        ("Ep10-Seq25-Sh123", 10, 25, 123),
    ])
    def test_from_str_ok(self, s, ep, seq, sh):
        obj = ShotId.from_str(s)
        assert isinstance(obj, ShotId)
        assert (obj.episode, obj.sequence, obj.shot) == (ep, seq, sh)
        assert str(obj) == s

    @pytest.mark.parametrize("s", [
        "Ep1", "Ep1-Seq2", "Ep1-Seq2-Sh", "Ep-Seq2-Sh3", "Ep1-SeqA-Sh3", ""
    ])
    def test_from_str_err(self, s):
        with pytest.raises(ValueError) as e:
            ShotId.from_str(s)
        assert "Invalid ShotId" in str(e.value)

    def test_parent(self):
        sh = ShotId.from_str("Ep2-Seq4-Sh6")
        parent = sh.parent()
        assert isinstance(parent, SequenceId)
        assert str(parent) == "Ep2-Seq4"

# ---------- Factory parse() ---------------------------------------------------
class TestHierarchyParse:
    @pytest.mark.parametrize("s,cls_", [
        ("Ep5", EpisodeId),
        ("Ep5-Seq1", SequenceId),
        ("Ep5-Seq1-Sh9", ShotId),
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
            hierarchy_id=ShotId.from_str("Ep1-Seq2-Sh3"),
        )
        assert isinstance(dto.hierarchy_id, ShotId)

    def test_shotdto_rejects_other_hierarchy_types(self):
        with pytest.raises(TypeError) as e1:
            ShotDTO(
                id=UUID(int=2),
                title="t",
                style="s",
                text="x",
                hierarchy_id=SequenceId.from_str("Ep1-Seq2"), # type: ignore[arg-type]
            )
        assert "Expected ShotId, got SequenceId" in str(e1.value)

        with pytest.raises(TypeError) as e2:
            ShotDTO(
                id=UUID(int=3),
                title="t",
                style="s",
                text="x",
                hierarchy_id=EpisodeId.from_str("Ep1"), # type: ignore[arg-type]
            )
        assert "Expected ShotId, got EpisodeId" in str(e2.value)

    @pytest.mark.parametrize("s", [
        "Ep0-Seq0-Sh0",
        "Ep1-Seq2-Sh3",
        "Ep10-Seq25-Sh123",
    ])
    def test_shotdto_accepts_string_and_parses(self, s):
        dto = ShotDTO(
            id=UUID(int=4),
            title="t",
            style="s",
            text="x",
            hierarchy_id=s, # type: ignore[arg-type]
        )
        assert isinstance(dto.hierarchy_id, ShotId)
        assert str(dto.hierarchy_id) == s

    def test_sequencedto_and_episodedto_strictness(self):
        seq = SequenceDTO(
            id=UUID(int=5),
            title="seq",
            style="styl",
            shots=[],
            hierarchy_id="Ep2-Seq7", # type: ignore[arg-type]
        )
        assert isinstance(seq.hierarchy_id, SequenceId)

        ep = EpisodeDTO(
            id=UUID(int=6),
            title="ep",
            style="x",
            sequences=[],
            hierarchy_id="Ep9", # type: ignore[arg-type]
        )
        assert isinstance(ep.hierarchy_id, EpisodeId)

        # Wrong depth should fail
        with pytest.raises(TypeError):
            SequenceDTO(
                id=UUID(int=7),
                title="bad",
                style="x",
                shots=[],
                hierarchy_id=ShotId.from_str("Ep1-Seq1-Sh1"),
            )
        with pytest.raises(TypeError):
            EpisodeDTO(
                id=UUID(int=8),
                title="bad",
                sequences=[],
                hierarchy_id=SequenceId.from_str("Ep1-Seq1"),
            ) # type: ignore[arg-type]

# ---------- Using mocker to assert from_str is called -------------------------
class TestValidatorWithMocker:
    def test_shotdto_calls_from_str_for_string(self, mocker):
        spy = mocker.spy(ShotId, "from_str")
        s = "Ep3-Seq4-Sh5"
        dto = ShotDTO(
            id=UUID(int=9),
            title="t",
            style="s",
            text="x",
            hierarchy_id=s, # type: ignore[arg-type]
        )
        assert isinstance(dto.hierarchy_id, ShotId)
        spy.assert_called_once_with(s)

    def test_episodedto_calls_from_str_for_string(self, mocker):
        spy = mocker.spy(EpisodeId, "from_str")
        s = "Ep42"
        dto = EpisodeDTO(
            id=UUID(int=10),
            title="t",
            sequences=[],
            hierarchy_id=s, # type: ignore[arg-type]
            style="s"
        )
        assert isinstance(dto.hierarchy_id, EpisodeId)
        spy.assert_called_once_with(s)

# ---------- Test project -------------------------

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

    @pytest.mark.parametrize("s", [
        "", "Pr", "Pr-1", "PrA", "Ep1", "Seq1", "Pr1-Seq2"
    ])
    def test_from_str_err(self, s):
        # Invalid formats must raise ValueError
        with pytest.raises(ValueError):
            ProjectId.from_str(s)

    def test_parse_ok_with_mocker(self, mocker):
        # Ensure HierarchyId.parse dispatches to ProjectId.from_str
        spy = mocker.spy(ProjectId, "from_str")
        obj = HierarchyId.parse("Pr7")
        assert isinstance(obj, ProjectId)
        assert str(obj) == "Pr7"
        spy.assert_called_once_with("Pr7")

    @pytest.mark.parametrize("s", ["Epx", "random", "Ep1-Seq", "Sh1"])
    def test_parse_err(self, s):
        # Non-matching strings must raise ValueError
        with pytest.raises(ValueError):
            HierarchyId.parse(s)


class TestProjectDTO:
    def test_accepts_projectid_instance(self):
        # Accept a ProjectId instance as-is
        dto = ProjectDTO(
            episodes=[],
            hierarchy_id=ProjectId.from_str("Pr2"),
        )
        assert isinstance(dto.hierarchy_id, ProjectId)
        assert dto.hierarchy_id.project == 2

    def test_accepts_projectid_dict(self):
        # Pydantic should construct ProjectId from a dict payload
        dto = ProjectDTO(
            episodes=[],
            hierarchy_id={"project": 3},
        )
        assert isinstance(dto.hierarchy_id, ProjectId)
        assert dto.hierarchy_id.project == 3

    def test_rejects_string(self):
        # Strings are not accepted for ProjectDTO (no validator here)
        with pytest.raises(ValidationError):
            ProjectDTO(
                episodes=[],
                hierarchy_id="Pr4",
            )

    @pytest.mark.parametrize("wrong", [
        EpisodeId.from_str("Ep1"),
        SequenceId.from_str("Ep1-Seq2"),
        ShotId.from_str("Ep1-Seq2-Sh3"),
    ])
    def test_rejects_other_id_models(self, wrong):
        # Strict type: only ProjectId is allowed
        with pytest.raises(ValidationError):
            ProjectDTO(
                episodes=[],
                hierarchy_id=wrong,
            )

    def test_dump_shape(self):
        # Without a field serializer, the submodel is dumped as a dict
        dto = ProjectDTO(episodes=[], hierarchy_id=ProjectId.from_str("Pr9"))
        dumped = dto.model_dump()
        assert dumped["hierarchy_id"] == {"project": 9}
from __future__ import annotations

import asyncio
import os
import sys
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Callable, Mapping, MutableMapping

from botocore.exceptions import ClientError
from moviepy import AudioFileClip, CompositeVideoClip, ImageClip, concatenate_videoclips

# Make the DTO and saver packages available without requiring installation
ROOT_DIR = Path(__file__).resolve().parents[4]
DTO_SRC = ROOT_DIR / "dto" / "src"
ASSETS_SRC = ROOT_DIR / "assets_service" / "src"

for module_path in (DTO_SRC, ASSETS_SRC):
    if module_path.is_dir():
        path_str = str(module_path)
        if path_str not in sys.path:
            sys.path.append(path_str)

from scenario_dto.dto import ProjectDTO  # pylint: disable=wrong-import-position
from saver.s3_saver import S3AsyncSaver  # pylint: disable=wrong-import-position

FPS = 30
DEFAULT_S3_ENDPOINT = os.getenv("S3_ENDPOINT_URL", "http://127.0.0.1:9000")
DEFAULT_S3_ACCESS_KEY = os.getenv("S3_ACCESS_KEY", "minio")
DEFAULT_S3_SECRET_KEY = os.getenv("S3_SECRET_KEY", "minio123")
DEFAULT_S3_REGION = os.getenv("S3_REGION", "us-east-1")
DEFAULT_S3_BUCKET = os.getenv("S3_BUCKET", "demo")


class S3AssetCollector:
    """Collect and download S3 assets derived from arbitrary DTO objects."""

    def __init__(self, base_dir: Path):
        self._base_dir = base_dir
        self._targets: MutableMapping[str, Path] = {}

    @staticmethod
    def _sequence_image_key(sequence_id) -> str:
        name = str(sequence_id)
        return f"{name.replace('-', '/')}/{name}.png"

    @staticmethod
    def _shot_audio_key(shot_id) -> str:
        name = str(shot_id)
        return f"{name.replace('-', '/')}/{name}.wav"

    def add_asset(self, dto, key_builder: Callable[[object], str]) -> Path:
        """Register a DTO to download using the provided key builder."""

        key = key_builder(dto)
        destination = self._base_dir / key
        if key not in self._targets:
            self._targets[key] = destination
        return destination

    async def download(
        self,
        *,
        bucket: str,
        endpoint_url: str,
        access_key: str,
        secret_key: str,
        region: str,
    ) -> dict[str, Path]:
        if not self._targets:
            return {}

        async with S3AsyncSaver(
            bucket=bucket,
            endpoint_url=endpoint_url,
            access_key=access_key,
            secret_key=secret_key,
            region=region,
        ) as saver:
            downloaded: dict[str, Path] = {}
            for key, destination in self._targets.items():
                if not destination.exists():
                    destination.parent.mkdir(parents=True, exist_ok=True)
                    try:
                        data = await saver.download(key)
                    except ClientError as exc:  # pragma: no cover - defensive
                        raise FileNotFoundError(
                            f"Asset '{key}' not found in bucket '{bucket}'"
                        ) from exc
                    destination.write_bytes(data)
                downloaded[key] = destination
        return downloaded

    @property
    def targets(self) -> Mapping[str, Path]:
        return dict(self._targets)


def render_project(
    project: ProjectDTO,
    *,
    bucket: str = DEFAULT_S3_BUCKET,
    endpoint_url: str = DEFAULT_S3_ENDPOINT,
    access_key: str = DEFAULT_S3_ACCESS_KEY,
    secret_key: str = DEFAULT_S3_SECRET_KEY,
    region: str = DEFAULT_S3_REGION,
    output: str | Path = "output.mp4",
) -> Path:
    """Render a project into a video using assets stored in S3."""

    if not project.episodes:
        raise ValueError("Project does not contain any episodes to render")

    output_path = Path(output)

    with TemporaryDirectory() as tmpdir_name:
        tmpdir = Path(tmpdir_name)
        collector = S3AssetCollector(tmpdir)
        has_shots = False

        for episode in project.episodes:
            for sequence in episode.sequences:
                collector.add_asset(
                    sequence.hierarchy_id,
                    S3AssetCollector._sequence_image_key,
                )
                for shot in sequence.shots:
                    has_shots = True
                    collector.add_asset(
                        shot.hierarchy_id,
                        S3AssetCollector._shot_audio_key,
                    )

        if not has_shots:
            raise ValueError("Project does not contain any shots to render")

        downloaded_assets = asyncio.run(
            collector.download(
                bucket=bucket,
                endpoint_url=endpoint_url,
                access_key=access_key,
                secret_key=secret_key,
                region=region,
            )
        )

        clips: list[CompositeVideoClip] = []
        audio_clips: list[AudioFileClip] = []

        for episode in sorted(project.episodes, key=lambda ep: ep.hierarchy_id.episode):
            for sequence in sorted(episode.sequences, key=lambda seq: seq.hierarchy_id.sequence):
                image_key = S3AssetCollector._sequence_image_key(sequence.hierarchy_id)
                image_path = downloaded_assets[image_key]
                for shot in sorted(sequence.shots, key=lambda sh: sh.hierarchy_id.shot):
                    audio_key = S3AssetCollector._shot_audio_key(shot.hierarchy_id)
                    audio_path = downloaded_assets[audio_key]
                    audio_clip = AudioFileClip(str(audio_path))
                    audio_clips.append(audio_clip)
                    clip = (
                        ImageClip(str(image_path))
                        .with_duration(audio_clip.duration)
                        .with_audio(audio_clip)
                        .with_fps(FPS)
                        .resized(height=1080)
                    )
                    frame = CompositeVideoClip(
                        [clip.with_position("center")],
                        size=(1920, 1080),
                        bg_color=(0, 0, 0),
                    )
                    clips.append(frame)

        final = concatenate_videoclips(clips, method="chain")
        final.write_videofile(str(output_path), fps=FPS, codec="libx264", audio_codec="aac")
        final.close()

        for clip in clips:
            clip.close()
        for audio_clip in audio_clips:
            audio_clip.close()

    return output_path


__all__ = ["render_project"]

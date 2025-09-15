import asyncio
import io
import os
from typing import Optional

import numpy as np
import torch
import soundfile as sf
from pydub import AudioSegment, effects

try:  # pragma: no cover - import error is handled at runtime
    from assets_service.src.saver.s3_saver import S3AsyncSaver
    _S3_IMPORT_ERROR = None
except ModuleNotFoundError as exc:  # pragma: no cover - makes runtime error explicit
    S3AsyncSaver = None  # type: ignore
    _S3_IMPORT_ERROR = exc


class SileroTTSProcessor:
    """
    Wrapper for Silero TTS model with utilities for speech synthesis,
    normalization, speed adjustment, and optional reverb.
    """

    def __init__(
        self,
        speaker: str = "eugene",
        sample_rate: int = 48000,
        *,
        bucket: Optional[str] = None,
        endpoint_url: Optional[str] = None,
        access_key: Optional[str] = None,
        secret_key: Optional[str] = None,
        region: Optional[str] = None,
        root_prefix: Optional[str] = None,
    ):
        self.speaker = speaker
        self.sample_rate = sample_rate

        if S3AsyncSaver is None:  # pragma: no cover - handled at runtime if dependency missing
            raise RuntimeError(
                "S3AsyncSaver is unavailable. Ensure assets_service dependencies are installed"
            ) from _S3_IMPORT_ERROR

        bucket = bucket or os.getenv("TTS_S3_BUCKET", "genvideoai-tts")
        endpoint_url = endpoint_url or os.getenv("TTS_S3_ENDPOINT", "http://127.0.0.1:9000")
        access_key = access_key or os.getenv("TTS_S3_ACCESS_KEY", "minio")
        secret_key = secret_key or os.getenv("TTS_S3_SECRET_KEY", "minio123")
        region = region or os.getenv("TTS_S3_REGION", "us-east-1")
        root_prefix = root_prefix or os.getenv("TTS_S3_ROOT_PREFIX", "")

        self.bucket = bucket
        self.root_prefix = root_prefix.strip("/") if root_prefix else ""
        self._s3_config = dict(
            bucket=bucket,
            endpoint_url=endpoint_url,
            access_key=access_key,
            secret_key=secret_key,
            region=region,
        )

        # load the Silero TTS model once
        self.model, _ = torch.hub.load(
            repo_or_dir="snakers4/silero-models",
            model="silero_tts",
            language="ru",
            speaker="v3_1_ru"
        )

    def synthesize(self, text: str) -> any:
        """
        Generate raw audio waveform (numpy array) from text.
        """
        audio = self.model.apply_tts(
            text=text,
            speaker=self.speaker,
            sample_rate=self.sample_rate,
            put_accent=True,
            put_yo=True,
        )
        return audio.numpy()

    async def save_audio(
        self,
        audio,
        hierarchy_id: str,
        *,
        variant: str = "raw",
    ) -> str:
        """
        Save audio waveform to S3 using hierarchy-based key.
        """
        async with S3AsyncSaver(**self._s3_config) as saver:
            wav_bytes = await self._resolve_audio_bytes(
                audio, hierarchy_id, None, saver
            )
            key = self._build_s3_key(hierarchy_id, suffix=variant)
            await saver.save(wav_bytes, key, content_type="audio/wav")
        print(f"Raw audio saved to s3://{self.bucket}/{key}")
        return key

    async def process_audio(
        self,
        audio,
        hierarchy_id: str,
        speed: float = 0.9,
        reverb: bool = True,
        *,
        variant: Optional[str] = None,
        source_variant: str = "raw",
    ) -> str:
        """
        Normalize loudness, adjust speed, optionally add reverb, and upload to S3.
        """
        async with S3AsyncSaver(**self._s3_config) as saver:
            wav_bytes = await self._resolve_audio_bytes(
                audio, hierarchy_id, source_variant, saver
            )
            sound = AudioSegment.from_file(io.BytesIO(wav_bytes), format="wav")

            # normalize loudness
            sound = effects.normalize(sound)

            # adjust playback speed (tempo)
            sound = sound._spawn(
                sound.raw_data,
                overrides={"frame_rate": int(sound.frame_rate * speed)}
            ).set_frame_rate(sound.frame_rate)

            # add light reverb (simulated with echo overlay)
            if reverb:
                delay = 120   # milliseconds
                decay = -20   # echo volume (dB)
                echo = sound.overlay(sound - abs(decay), position=delay)
                sound = echo

            buffer = io.BytesIO()
            sound.export(buffer, format="wav")
            buffer.seek(0)

            key = self._build_s3_key(hierarchy_id, suffix=variant)
            await saver.save(buffer.read(), key, content_type="audio/wav")

        print(
            f"Processed audio saved to s3://{self.bucket}/{key} "
            f"(speed={speed}, reverb={reverb})"
        )
        return key

    def _build_s3_key(self, hierarchy_id: str, *, suffix: Optional[str] = None, extension: str = "wav") -> str:
        clean_id = str(hierarchy_id).strip()
        if clean_id.lower().endswith(f".{extension.lower()}"):
            clean_id = clean_id[: -(len(extension) + 1)]

        segments = [seg for seg in clean_id.split("-") if seg]
        if not segments:
            raise ValueError("hierarchy_id must contain at least one segment")

        path_parts = [self.root_prefix] if self.root_prefix else []
        path_parts.extend(segments)
        directory = "/".join(path_parts)

        filename = clean_id
        if suffix:
            filename = f"{filename}_{suffix}"

        return f"{directory}/{filename}.{extension}"

    async def _resolve_audio_bytes(
        self,
        audio,
        hierarchy_id: Optional[str] = None,
        source_variant: Optional[str] = None,
        saver: Optional["S3AsyncSaver"] = None,
    ) -> bytes:
        if audio is None:
            if hierarchy_id is None:
                raise ValueError("hierarchy_id is required when audio is None")
            key = self._build_s3_key(hierarchy_id, suffix=source_variant)
            if saver is None:
                raise RuntimeError("S3 saver is required to download audio")
            return await saver.download(key)

        if isinstance(audio, np.ndarray):
            return self._numpy_to_wav_bytes(audio)

        if isinstance(audio, (bytes, bytearray)):
            return bytes(audio)

        if isinstance(audio, AudioSegment):
            buffer = io.BytesIO()
            audio.export(buffer, format="wav")
            return buffer.getvalue()

        if isinstance(audio, io.IOBase):
            position = audio.tell() if audio.seekable() else None
            try:
                audio.seek(0)
            except (OSError, AttributeError):
                pass
            data = audio.read()
            if position is not None:
                try:
                    audio.seek(position)
                except (OSError, AttributeError):
                    pass
            return data

        if isinstance(audio, str):
            if os.path.exists(audio):
                with open(audio, "rb") as f:
                    return f.read()
            if saver is None:
                raise RuntimeError("S3 saver is required to download audio")
            return await saver.download(audio)

        raise TypeError(f"Unsupported audio type: {type(audio)!r}")

    def _numpy_to_wav_bytes(self, audio) -> bytes:
        buffer = io.BytesIO()
        sf.write(buffer, audio, self.sample_rate, format="wav")
        buffer.seek(0)
        return buffer.read()


async def _demo() -> None:
    text = """Легенда о Ромуле и Реме задаёт тон ранней истории Рима.
    Археологические данные напоминают, что город возник в ходе постепенного сосуществования латинских поселений.
    Социальные и политические институты начали формироваться здесь, на перекрёстке торговли и обороны."""

    tts = SileroTTSProcessor(speaker="eugene")

    # synthesis
    audio = tts.synthesize(text)

    hierarchy_id = "Pr0-Ep0-Seq0"

    # save raw audio to S3
    await tts.save_audio(audio, hierarchy_id, variant="raw")

    # normalize, change speed, add reverb and store the final asset in S3
    await tts.process_audio(None, hierarchy_id, speed=0.9, reverb=True)


if __name__ == "__main__":
    asyncio.run(_demo())

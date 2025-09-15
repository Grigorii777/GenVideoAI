import aioboto3
from pathlib import Path
from typing import Optional
from botocore.config import Config
from botocore.exceptions import ClientError

class S3AsyncSaver:
    def __init__(
        self,
        *,
        bucket: str,
        endpoint_url: str = "http://127.0.0.1:9000",
        access_key: str = "minio",
        secret_key: str = "minio123",
        region: str = "us-east-1",
    ):
        self.bucket = bucket
        self._session = aioboto3.Session()
        self._client_kwargs = dict(
            endpoint_url=endpoint_url,
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            region_name=region,
            config=Config(s3={"addressing_style": "path"}),
        )
        self._cm = None
        self._s3 = None

    async def __aenter__(self):
        self._cm = self._session.client("s3", **self._client_kwargs)
        self._s3 = await self._cm.__aenter__()
        await self._ensure_bucket()
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return await self._cm.__aexit__(exc_type, exc, tb)

    async def _ensure_bucket(self):
        try:
            await self._s3.head_bucket(Bucket=self.bucket)
        except ClientError:
            await self._s3.create_bucket(Bucket=self.bucket)

    async def save(self, data: bytes, key: str, *, content_type: Optional[str] = None):
        if content_type is None:
            ext = Path(key).suffix.lower()
            content_type = {
                ".png": "image/png",
                ".jpg": "image/jpeg",
                ".jpeg": "image/jpeg",
                ".webp": "image/webp",
                ".wav": "audio/wav",
                ".yaml": "application/x-yaml",
                ".yml": "application/x-yaml",
            }.get(ext, "application/octet-stream")
        await self._s3.put_object(Bucket=self.bucket, Key=key, Body=data, ContentType=content_type)

    async def download(self, key: str) -> bytes:
        response = await self._s3.get_object(Bucket=self.bucket, Key=key)
        async with response["Body"] as stream:
            return await stream.read()

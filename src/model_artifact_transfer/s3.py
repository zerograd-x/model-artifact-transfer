from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import boto3


@dataclass(frozen=True)
class S3Destination:
    """Publish a local artifact tree to one S3 prefix."""

    bucket: str
    prefix: str = ""
    client: Any | None = None

    def __post_init__(self) -> None:
        if (
            not self.bucket
            or not self.bucket.strip()
            or self.bucket != self.bucket.strip()
            or "/" in self.bucket
        ):
            raise ValueError("bucket must be a non-empty S3 bucket name")
        normalized = self.prefix.strip("/")
        object.__setattr__(self, "prefix", normalized)

    @classmethod
    def from_uri(
        cls,
        uri: str,
        *,
        client: Any | None = None,
    ) -> "S3Destination":
        parsed = urlparse(uri)
        if parsed.scheme != "s3" or not parsed.netloc:
            raise ValueError("S3 URI must have the form s3://bucket[/prefix]")
        if parsed.params or parsed.query or parsed.fragment:
            raise ValueError("S3 URI must not contain params, query, or fragment")
        return cls(
            bucket=parsed.netloc,
            prefix=parsed.path.strip("/"),
            client=client,
        )

    @property
    def uri(self) -> str:
        suffix = f"/{self.prefix}" if self.prefix else ""
        return f"s3://{self.bucket}{suffix}"

    def _client(self):
        return self.client or boto3.client("s3")

    def _object_key(self, relative_path: str) -> str:
        relative = relative_path.replace("\\", "/").lstrip("/")
        return f"{self.prefix}/{relative}" if self.prefix else relative

    def _prefix_exists(self, client: Any) -> bool:
        prefix = f"{self.prefix}/" if self.prefix else ""
        response = client.list_objects_v2(
            Bucket=self.bucket,
            Prefix=prefix,
            MaxKeys=1,
        )
        return bool(response.get("Contents"))

    def publish(self, local_dir: str) -> None:
        root = Path(local_dir)
        if not root.is_dir():
            raise ValueError(f"Source artifact is not a directory: {local_dir}")

        files = sorted(path for path in root.rglob("*") if path.is_file())
        if not files:
            raise ValueError(f"Source artifact contains no files: {local_dir}")

        client = self._client()
        if self._prefix_exists(client):
            raise FileExistsError(
                f"Destination already contains objects: {self.uri}"
            )

        for path in files:
            relative = path.relative_to(root).as_posix()
            client.upload_file(
                str(path),
                self.bucket,
                self._object_key(relative),
            )

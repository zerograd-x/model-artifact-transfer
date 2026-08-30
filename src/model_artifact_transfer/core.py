from __future__ import annotations

from tempfile import TemporaryDirectory
from typing import Protocol


class ArtifactSource(Protocol):
    """Materializes an artifact into a caller-provided local directory."""

    def materialize(self, local_dir: str) -> None: ...


class ArtifactDestination(Protocol):
    """Publishes a fully materialized local artifact tree."""

    def publish(self, local_dir: str) -> None: ...


def transfer_artifact(
    source: ArtifactSource,
    destination: ArtifactDestination,
    *,
    staging_name: str = "artifact",
) -> None:
    """Transfer one artifact through a temporary local staging directory.

    The source and destination are intentionally storage-agnostic. A source
    first materializes the complete artifact locally; only then is the tree
    published to the destination.
    """
    if not staging_name or "/" in staging_name or "\\" in staging_name:
        raise ValueError("staging_name must be a non-empty path component")

    with TemporaryDirectory() as tmp_dir:
        local_dir = f"{tmp_dir}/{staging_name}"
        source.materialize(local_dir)
        destination.publish(local_dir)

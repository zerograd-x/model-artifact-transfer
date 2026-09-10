from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import shutil


@dataclass(frozen=True)
class LocalDirectoryDestination:
    """Publish a staged artifact tree to a local filesystem directory."""

    path: str
    overwrite: bool = False

    def publish(self, local_dir: str) -> None:
        source = Path(local_dir)
        if not source.is_dir():
            raise ValueError(f"Source artifact is not a directory: {local_dir}")

        destination = Path(self.path)
        if destination.exists():
            if not self.overwrite:
                raise FileExistsError(
                    f"Destination already exists: {destination}"
                )
            if destination.is_dir() and not destination.is_symlink():
                shutil.rmtree(destination)
            else:
                destination.unlink()

        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(source, destination)

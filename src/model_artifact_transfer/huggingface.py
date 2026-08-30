from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from huggingface_hub import snapshot_download


@dataclass(frozen=True)
class HuggingFaceSource:
    repo_id: str
    revision: str | None = None
    snapshot_download_fn: Callable[..., str] = snapshot_download

    def materialize(self, local_dir: str) -> None:
        kwargs: dict[str, object] = {
            "repo_id": self.repo_id,
            "local_dir": local_dir,
        }
        if self.revision is not None:
            kwargs["revision"] = self.revision
        self.snapshot_download_fn(**kwargs)

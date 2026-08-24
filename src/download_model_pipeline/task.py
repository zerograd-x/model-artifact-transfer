from __future__ import annotations

import os
from tempfile import TemporaryDirectory
from typing import Any, Callable

from huggingface_hub import snapshot_download

from .config import DownloadModelConfig
from .storage_io import hdfs_upload_tree


def download_model(
    config: dict[str, Any],
    *,
    snapshot_download_fn: Callable[..., str] = snapshot_download,
    upload_tree_fn: Callable[..., None] = hdfs_upload_tree,
) -> dict[str, str]:
    """Download one Hugging Face repository and upload it to HDFS.

    Current behavior:
    no revision pin, no token, no file filtering, no cache/resume layer, and the
    staging directory name is derived from hdfs_path rather than hf_repo_id.
    """
    cfg = DownloadModelConfig.model_validate(config)
    model_name = cfg.hdfs_path.rstrip("/").rsplit("/", 1)[-1]

    with TemporaryDirectory() as tmp_dir:
        local_model_dir = os.path.join(tmp_dir, model_name)
        os.makedirs(local_model_dir, exist_ok=True)

        snapshot_download_fn(repo_id=cfg.hf_repo_id, local_dir=local_model_dir)
        upload_tree_fn(
            local_model_dir,
            cfg.hdfs_path,
            max_workers=cfg.upload_parallelism,
        )

    return {"hdfs_path": cfg.hdfs_path, "hf_repo_id": cfg.hf_repo_id}

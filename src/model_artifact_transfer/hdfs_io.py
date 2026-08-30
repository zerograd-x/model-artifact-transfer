from __future__ import annotations

import os
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Callable


class HdfsError(RuntimeError):
    """Raised when an HDFS operation fails."""


_TRUTHY = {"1", "true", "yes", "on"}
_FALSY = {"0", "false", "no", "off"}


def hdfs_overwrite_enabled() -> bool:
    raw = os.environ.get("HDFS_OVERWRITE")
    if raw is None:
        return False
    value = raw.strip().lower()
    if value in _TRUTHY:
        return True
    if value in _FALSY:
        return False
    raise ValueError(
        "HDFS_OVERWRITE must be one of "
        f"{sorted(_TRUTHY | _FALSY)}; got {raw!r}"
    )


def _run_hdfs(args: list[str]) -> None:
    try:
        subprocess.run(
            ["hdfs", "dfs", *args],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
    except FileNotFoundError as exc:
        raise HdfsError("'hdfs' executable was not found on PATH") from exc
    except subprocess.CalledProcessError as exc:
        stderr = (exc.stderr or "").strip()
        raise HdfsError(
            f"hdfs dfs {' '.join(args)} failed with exit code {exc.returncode}: {stderr}"
        ) from exc


def _hdfs_put_file(local_path: str, remote_dir: str) -> None:
    args = ["-put"]
    if hdfs_overwrite_enabled():
        args.append("-f")
    args.extend([local_path, remote_dir])
    _run_hdfs(args)


def _remote_join(root: str, rel_path: str) -> str:
    return root.rstrip("/") + "/" + rel_path.replace(os.sep, "/").lstrip("/")


def hdfs_upload_tree(
    src_path: str,
    dest_path: str,
    *,
    max_workers: int = 16,
    put_file: Callable[[str, str], None] = _hdfs_put_file,
    mkdir: Callable[[str], None] | None = None,
) -> None:
    src = Path(src_path)
    if not src.is_dir():
        raise HdfsError(f"Source path is not a directory: {src_path}")
    if max_workers < 1:
        raise ValueError("max_workers must be >= 1")

    files: list[tuple[str, str, int]] = []
    remote_dirs: set[str] = {dest_path.rstrip("/")}
    total_bytes = 0
    for root, _dirs, names in os.walk(src_path):
        for name in names:
            local_file = os.path.join(root, name)
            rel_path = os.path.relpath(local_file, src_path)
            size = os.path.getsize(local_file)
            files.append((local_file, rel_path, size))
            total_bytes += size
            rel_dir = os.path.dirname(rel_path)
            if rel_dir and rel_dir != ".":
                remote_dirs.add(_remote_join(dest_path, rel_dir))

    if not files:
        raise HdfsError(f"No files found under {src_path}")

    mkdir_fn = mkdir or (lambda path: _run_hdfs(["-mkdir", "-p", path]))
    for remote_dir in sorted(remote_dirs):
        mkdir_fn(remote_dir)

    errors: list[Exception] = []
    completed = 0
    uploaded_bytes = 0

    def upload_one(item: tuple[str, str, int]) -> tuple[str, int]:
        local_file, rel_path, size = item
        rel_dir = os.path.dirname(rel_path)
        remote_dir = (
            dest_path.rstrip("/")
            if not rel_dir or rel_dir == "."
            else _remote_join(dest_path, rel_dir)
        )
        put_file(local_file, remote_dir)
        return rel_path, size

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_item = {executor.submit(upload_one, item): item for item in files}
        for future in as_completed(future_to_item):
            _local_file, rel_path, _size = future_to_item[future]
            try:
                finished_rel_path, size = future.result()
                completed += 1
                uploaded_bytes += size
                print(
                    f"Uploaded {completed}/{len(files)} files "
                    f"({uploaded_bytes / 2**30:.1f}/{total_bytes / 2**30:.1f} GiB): "
                    f"{finished_rel_path}"
                )
            except Exception as exc:
                errors.append(exc)
                print(f"Upload failed for {rel_path}: {exc}")

    if errors:
        raise HdfsError(
            f"Failed to upload {len(errors)} file(s); first error: {errors[0]}"
        )

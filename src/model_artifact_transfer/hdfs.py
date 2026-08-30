from __future__ import annotations

from dataclasses import dataclass

from .hdfs_io import hdfs_upload_tree


@dataclass(frozen=True)
class HdfsDestination:
    path: str
    parallelism: int = 16

    def publish(self, local_dir: str) -> None:
        hdfs_upload_tree(local_dir, self.path, max_workers=self.parallelism)

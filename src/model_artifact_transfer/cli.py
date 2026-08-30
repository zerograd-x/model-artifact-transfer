from __future__ import annotations

import argparse
import os

from .core import transfer_artifact
from .hdfs import HdfsDestination
from .huggingface import HuggingFaceSource


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Transfer a model artifact between storage backends."
    )
    parser.add_argument("--hf-repo-id", required=True)
    parser.add_argument("--hdfs-path", required=True)
    parser.add_argument("--revision")
    parser.add_argument("--upload-parallelism", type=int, default=16)
    parser.add_argument("--overwrite", action="store_true")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    if args.overwrite:
        os.environ["HDFS_OVERWRITE"] = "true"

    staging_name = args.hdfs_path.rstrip("/").rsplit("/", 1)[-1]
    transfer_artifact(
        HuggingFaceSource(args.hf_repo_id, revision=args.revision),
        HdfsDestination(args.hdfs_path, parallelism=args.upload_parallelism),
        staging_name=staging_name,
    )


if __name__ == "__main__":
    main()

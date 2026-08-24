from __future__ import annotations

import argparse
import json
import os

from .task import download_model


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Download one Hugging Face repo and upload it to HDFS."
    )
    parser.add_argument("--hf-repo-id", required=True)
    parser.add_argument("--hdfs-path", required=True)
    parser.add_argument("--upload-parallelism", type=int, default=16)
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Set HDFS_OVERWRITE=true for this process (adds hdfs dfs -put -f).",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    if args.overwrite:
        os.environ["HDFS_OVERWRITE"] = "true"

    result = download_model(
        {
            "hf_repo_id": args.hf_repo_id,
            "hdfs_path": args.hdfs_path,
            "upload_parallelism": args.upload_parallelism,
        }
    )
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()

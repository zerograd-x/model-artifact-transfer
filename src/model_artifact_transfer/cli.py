from __future__ import annotations

import argparse

from .core import transfer_artifact
from .huggingface import HuggingFaceSource
from .s3 import S3Destination


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Transfer a Hugging Face model artifact to Amazon S3."
    )
    parser.add_argument("--hf-repo-id", required=True)
    parser.add_argument("--s3-uri", required=True)
    parser.add_argument("--revision")
    parser.add_argument("--staging-name")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    staging_name = args.staging_name or args.hf_repo_id.rstrip("/").rsplit("/", 1)[-1]
    transfer_artifact(
        HuggingFaceSource(args.hf_repo_id, revision=args.revision),
        S3Destination.from_uri(args.s3_uri),
        staging_name=staging_name,
    )


if __name__ == "__main__":
    main()

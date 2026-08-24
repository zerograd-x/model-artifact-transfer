# download-model-pipeline

A small, portable pipeline for downloading a Hugging Face model repository to a
temporary local directory and uploading the resulting directory tree to HDFS.

```text
config -> workflow -> download task
                     |-> snapshot_download() to temporary local storage
                     `-> parallel hdfs dfs -put to the destination
```

The implementation is intentionally simple:

- one model repository is processed per invocation;
- config fields are `hf_repo_id`, `hdfs_path`, and `upload_parallelism` (default 16);
- the local staging directory name is derived from the destination path;
- the full Hugging Face repository is downloaded before upload begins;
- `HDFS_OVERWRITE` is read for each file upload;
- file uploads run concurrently;
- upload failures are collected and reported after all submitted uploads finish;
- a failed upload can leave a partially populated destination;
- there is no revision pinning, skip-if-exists, resume, rollback, or automatic
  repo/path consistency check.

## Requirements

- Python 3.9+
- `hdfs` CLI available on `PATH` for real uploads
- network/authentication configured so `huggingface_hub.snapshot_download` can access
  the target repository

## Install

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e '.[test]'
```

## Test

```bash
pytest
```

## Run

By default, uploads do not overwrite existing files:

```bash
download-model \
  --hf-repo-id Qwen/Qwen3-4B \
  --hdfs-path hdfs://example-cluster/models/Qwen3_4B_20260824
```

To allow replacement of existing files:

```bash
download-model \
  --hf-repo-id Qwen/Qwen3-4B \
  --hdfs-path hdfs://example-cluster/models/Qwen3_4B_20260824 \
  --overwrite
```

`--overwrite` sets `HDFS_OVERWRITE=true`, causing file uploads to use
`hdfs dfs -put -f`.

## Package layout

```text
src/download_model_pipeline/
  config.py       # Pydantic configuration
  workflow.py     # one-task workflow entry point
  task.py         # temporary staging + HF download + upload
  storage_io.py   # HDFS overwrite parsing and parallel tree upload
  cli.py          # command-line entry point

tests/
```

## Operational behavior

1. Reusing a destination while overwrite is enabled can replace existing files.
2. `hf_repo_id` and `hdfs_path` are not cross-validated.
3. Hugging Face `main` is not pinned to a revision.
4. Every run downloads and uploads the repository again.
5. Partial uploads can remain after failure.
6. Gated/private repositories depend on Hugging Face authentication in the runtime.
7. Every file in the Hugging Face repository is fetched.

See `docs/hardening.md` for optional production-safety improvements.

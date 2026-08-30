# model-artifact-transfer

A small, portable library for moving model artifact trees between storage backends through temporary local staging.

The public API is backend-oriented rather than pipeline-specific:

```text
ArtifactSource -> temporary local tree -> ArtifactDestination
```

The first concrete backends are:

- `HuggingFaceSource`: materializes a Hugging Face repository with `snapshot_download()`;
- `HdfsDestination`: publishes a local tree with parallel `hdfs dfs -put` operations.

Additional sources or destinations can implement the same small `materialize()` / `publish()` interfaces without changing the transfer core.

## Install

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e '.[test]'
```

## Python API

```python
from model_artifact_transfer import (
    HdfsDestination,
    HuggingFaceSource,
    transfer_artifact,
)

transfer_artifact(
    HuggingFaceSource("Qwen/Qwen3-4B", revision="main"),
    HdfsDestination(
        "hdfs://example-cluster/models/Qwen3_4B",
        parallelism=16,
    ),
    staging_name="Qwen3_4B",
)
```

## CLI

```bash
model-artifact-transfer \
  --hf-repo-id Qwen/Qwen3-4B \
  --hdfs-path hdfs://example-cluster/models/Qwen3_4B
```

Optional flags include `--revision`, `--upload-parallelism`, and `--overwrite`.
`--overwrite` sets `HDFS_OVERWRITE=true`, causing HDFS file uploads to use `hdfs dfs -put -f`.

## Tests

Unit tests do not access the network:

```bash
pytest
```

The integration test performs a real download of the small public `sshleifer/tiny-gpt2` repository through `HuggingFaceSource`, validates the staged model/tokenizer files, and uses an in-memory inspection destination rather than a real HDFS cluster:

```bash
pytest -o addopts='-q' -m integration tests/integration/test_real_hf_download.py
```

The real-download integration test also runs in GitHub Actions.

## Package layout

```text
src/model_artifact_transfer/
  core.py          # source/destination protocols and transfer orchestration
  huggingface.py   # Hugging Face source backend
  hdfs.py          # HDFS destination backend
  hdfs_io.py       # HDFS upload implementation
  cli.py           # command-line entry point
```

## Current behavior and limitations

- the complete source artifact is materialized before publishing begins;
- HDFS file uploads run concurrently;
- HDFS upload failures are collected after submitted uploads finish;
- a failed destination publish can leave a partially populated destination;
- there is no automatic resume, rollback, or skip-if-exists layer;
- gated/private Hugging Face repositories depend on authentication in the runtime;
- `HuggingFaceSource.revision` is optional, so callers should pin a revision when reproducibility matters.

See `docs/hardening.md` for production-safety considerations.

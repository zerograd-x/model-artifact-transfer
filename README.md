# model-artifact-transfer

A small library for moving complete model artifact trees between pluggable
sources and destinations through temporary local staging.

The transfer core is storage-neutral:

```text
ArtifactSource -> temporary local tree -> ArtifactDestination
```

The built-in endpoints are:

- `HuggingFaceSource`: materializes a Hugging Face repository with
  `snapshot_download()`;
- `S3Destination`: publishes the staged artifact tree to an Amazon S3 prefix.

Additional endpoints can implement the same small `materialize()` or
`publish()` protocols without changing the transfer core.

## Install

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e '.[test]'
```

AWS credentials use the standard boto3 credential chain.

## Python API

```python
from model_artifact_transfer import (
    HuggingFaceSource,
    S3Destination,
    transfer_artifact,
)

transfer_artifact(
    HuggingFaceSource(
        "Qwen/Qwen3-4B",
        revision="<pinned-revision>",
    ),
    S3Destination.from_uri(
        "s3://example-bucket/models/qwen3-4b/<version>"
    ),
    staging_name="qwen3-4b",
)
```

`S3Destination` treats the destination prefix as immutable. If any object
already exists under the prefix, publishing fails instead of partially
overwriting an older artifact. Use a new versioned prefix for a new artifact.

## CLI

```bash
model-artifact-transfer \
  --hf-repo-id Qwen/Qwen3-4B \
  --revision <pinned-revision> \
  --s3-uri s3://example-bucket/models/qwen3-4b/<version>
```

`--staging-name` is optional. By default it uses the final component of the
Hugging Face repository id.

## Tests

Unit tests do not require network or AWS access:

```bash
pytest
```

The integration test performs a real download of the small public
`sshleifer/tiny-gpt2` repository through `HuggingFaceSource`, validates the
staged files, and publishes only to an in-memory inspection destination:

```bash
pytest -o addopts='-q' -m integration \
  tests/integration/test_real_hf_download.py
```

## Package layout

```text
src/model_artifact_transfer/
  core.py          # source/destination protocols and transfer orchestration
  huggingface.py   # Hugging Face source
  s3.py            # S3 destination
  cli.py           # Hugging Face -> S3 command-line entry point
```

## Current behavior and limitations

- the complete source artifact is materialized locally before publishing starts;
- an existing S3 destination prefix is rejected;
- a failed S3 publish can leave a partially populated prefix;
- there is no automatic resume, rollback, manifest, or checksum verification yet;
- gated/private Hugging Face repositories require normal Hugging Face
  authentication;
- callers should pin `HuggingFaceSource.revision` when reproducibility matters.

See `docs/hardening.md` for the next production-safety improvements.

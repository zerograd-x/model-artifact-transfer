from pathlib import Path

import pytest

from download_model_pipeline.task import download_model


@pytest.mark.integration
def test_download_model_real_hugging_face_snapshot():
    """Download a tiny real HF repo, then validate the staged files before upload.

    HDFS is intentionally replaced with a local fake uploader so this test
    isolates the Hugging Face/network/staging half of the pipeline and can run
    on a normal GitHub-hosted CPU runner.
    """
    observed: dict[str, object] = {}

    def inspect_instead_of_upload(src: str, dest: str, *, max_workers: int) -> None:
        root = Path(src)
        assert root.is_dir()

        names = {path.name for path in root.rglob("*") if path.is_file()}

        # Core model metadata and GPT-2 tokenizer assets must be present.
        assert "config.json" in names
        assert "vocab.json" in names
        assert "merges.txt" in names

        # Accept either common Hugging Face weight format.
        assert {"model.safetensors", "pytorch_model.bin"} & names

        observed["files"] = names
        observed["dest"] = dest
        observed["max_workers"] = max_workers
        observed["staging_name"] = root.name

    result = download_model(
        {
            "hf_repo_id": "sshleifer/tiny-gpt2",
            "hdfs_path": "hdfs://integration-test/models/tiny-gpt2",
            "upload_parallelism": 2,
        },
        upload_tree_fn=inspect_instead_of_upload,
    )

    assert observed["dest"] == "hdfs://integration-test/models/tiny-gpt2"
    assert observed["max_workers"] == 2
    assert observed["staging_name"] == "tiny-gpt2"
    assert result == {
        "hdfs_path": "hdfs://integration-test/models/tiny-gpt2",
        "hf_repo_id": "sshleifer/tiny-gpt2",
    }

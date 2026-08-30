from pathlib import Path

import pytest

from model_artifact_transfer import HuggingFaceSource, transfer_artifact


class InspectDestination:
    def __init__(self):
        self.files: set[str] = set()
        self.staging_name: str | None = None

    def publish(self, local_dir: str) -> None:
        root = Path(local_dir)
        assert root.is_dir()

        names = {path.name for path in root.rglob("*") if path.is_file()}
        assert "config.json" in names
        assert "vocab.json" in names
        assert "merges.txt" in names
        assert {"model.safetensors", "pytorch_model.bin"} & names

        self.files = names
        self.staging_name = root.name


@pytest.mark.integration
def test_real_hugging_face_source_transfer():
    destination = InspectDestination()

    transfer_artifact(
        HuggingFaceSource("sshleifer/tiny-gpt2"),
        destination,
        staging_name="tiny-gpt2",
    )

    assert destination.staging_name == "tiny-gpt2"
    assert "config.json" in destination.files

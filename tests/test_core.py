from pathlib import Path

import pytest

from model_artifact_transfer import transfer_artifact


class FakeSource:
    def __init__(self):
        self.local_dir = None

    def materialize(self, local_dir: str) -> None:
        self.local_dir = local_dir
        root = Path(local_dir)
        root.mkdir(parents=True)
        (root / "config.json").write_text("{}")


class FakeDestination:
    def __init__(self):
        self.local_dir = None
        self.files = set()

    def publish(self, local_dir: str) -> None:
        self.local_dir = local_dir
        self.files = {p.name for p in Path(local_dir).iterdir() if p.is_file()}


def test_transfer_artifact_materializes_then_publishes():
    source = FakeSource()
    destination = FakeDestination()

    transfer_artifact(source, destination, staging_name="model-a")

    assert Path(source.local_dir).name == "model-a"
    assert source.local_dir == destination.local_dir
    assert destination.files == {"config.json"}
    assert not Path(source.local_dir).exists()


@pytest.mark.parametrize("name", ["", " ", ".", "..", "a/b", "a\\b"])
def test_transfer_artifact_rejects_invalid_staging_name(name):
    with pytest.raises(ValueError):
        transfer_artifact(FakeSource(), FakeDestination(), staging_name=name)

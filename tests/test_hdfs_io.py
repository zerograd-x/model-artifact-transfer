from pathlib import Path

import pytest

from model_artifact_transfer.hdfs_io import HdfsError, _hdfs_overwrite_enabled, hdfs_upload_tree


def test_overwrite_default_false(monkeypatch):
    monkeypatch.delenv("HDFS_OVERWRITE", raising=False)
    assert _hdfs_overwrite_enabled() is False


@pytest.mark.parametrize("value", ["1", "true", "TRUE", " yes ", "on"])
def test_overwrite_truthy(monkeypatch, value):
    monkeypatch.setenv("HDFS_OVERWRITE", value)
    assert _hdfs_overwrite_enabled() is True


@pytest.mark.parametrize("value", ["0", "false", "FALSE", " no ", "off"])
def test_overwrite_falsy(monkeypatch, value):
    monkeypatch.setenv("HDFS_OVERWRITE", value)
    assert _hdfs_overwrite_enabled() is False


def test_overwrite_invalid(monkeypatch):
    monkeypatch.setenv("HDFS_OVERWRITE", "enabled")
    with pytest.raises(ValueError):
        _hdfs_overwrite_enabled()


def test_empty_tree_fails(tmp_path):
    with pytest.raises(HdfsError, match="No files found"):
        hdfs_upload_tree(str(tmp_path), "hdfs://example-cluster/model", put_file=lambda *_: None)


def test_partial_failure_continues_then_raises(tmp_path):
    (tmp_path / "a.txt").write_text("a")
    (tmp_path / "b.txt").write_text("b")
    seen = []
    made_dirs = []

    def put_file(local_path, remote_dir):
        name = Path(local_path).name
        seen.append(name)
        if name == "a.txt":
            raise RuntimeError("boom")

    with pytest.raises(HdfsError, match="Failed to upload 1 file"):
        hdfs_upload_tree(
            str(tmp_path),
            "hdfs://example-cluster/model",
            max_workers=2,
            put_file=put_file,
            mkdir=made_dirs.append,
        )

    assert set(seen) == {"a.txt", "b.txt"}
    assert made_dirs == ["hdfs://example-cluster/model"]

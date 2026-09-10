from pathlib import Path

import pytest

from model_artifact_transfer import S3Destination


class FakeS3Client:
    def __init__(self, *, existing=False):
        self.existing = existing
        self.list_calls = []
        self.uploads = []

    def list_objects_v2(self, **kwargs):
        self.list_calls.append(kwargs)
        return {"Contents": [{"Key": "existing"}]} if self.existing else {}

    def upload_file(self, filename, bucket, key):
        self.uploads.append((Path(filename).name, bucket, key))


def test_s3_destination_from_uri():
    destination = S3Destination.from_uri("s3://example-bucket/models/model-a")

    assert destination.bucket == "example-bucket"
    assert destination.prefix == "models/model-a"
    assert destination.uri == "s3://example-bucket/models/model-a"


@pytest.mark.parametrize(
    "uri",
    ["", "https://example.com/model", "s3:///missing-bucket"],
)
def test_s3_destination_rejects_invalid_uri(uri):
    with pytest.raises(ValueError):
        S3Destination.from_uri(uri)


def test_s3_destination_uploads_tree_with_relative_keys(tmp_path):
    (tmp_path / "config.json").write_text("{}")
    weights = tmp_path / "weights"
    weights.mkdir()
    (weights / "part-00001.safetensors").write_text("weights")

    client = FakeS3Client()
    destination = S3Destination.from_uri(
        "s3://example-bucket/models/model-a",
        client=client,
    )
    destination.publish(str(tmp_path))

    assert client.list_calls == [
        {
            "Bucket": "example-bucket",
            "Prefix": "models/model-a/",
            "MaxKeys": 1,
        }
    ]
    assert client.uploads == [
        ("config.json", "example-bucket", "models/model-a/config.json"),
        (
            "part-00001.safetensors",
            "example-bucket",
            "models/model-a/weights/part-00001.safetensors",
        ),
    ]


def test_s3_destination_refuses_existing_prefix_by_default(tmp_path):
    (tmp_path / "config.json").write_text("{}")
    client = FakeS3Client(existing=True)

    destination = S3Destination(
        bucket="example-bucket",
        prefix="models/model-a",
        client=client,
    )

    with pytest.raises(FileExistsError, match="already contains"):
        destination.publish(str(tmp_path))
    assert client.uploads == []

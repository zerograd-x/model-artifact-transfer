import pytest
from pydantic import ValidationError

from download_model_pipeline.config import DownloadModelConfig


def test_required_fields():
    with pytest.raises(ValidationError):
        DownloadModelConfig.model_validate({})


def test_default_upload_parallelism():
    cfg = DownloadModelConfig(
        hf_repo_id="Qwen/Qwen3-4B",
        hdfs_path="hdfs://example-cluster/model",
    )
    assert cfg.upload_parallelism == 16


def test_upload_parallelism_must_be_positive():
    with pytest.raises(ValidationError):
        DownloadModelConfig(
            hf_repo_id="Qwen/Qwen3-4B",
            hdfs_path="hdfs://example-cluster/model",
            upload_parallelism=0,
        )


def test_model_dump_round_trip():
    cfg = DownloadModelConfig(
        hf_repo_id="Qwen/Qwen3-4B",
        hdfs_path="hdfs://example-cluster/Qwen3_4B_20260721",
        upload_parallelism=8,
    )
    assert DownloadModelConfig.model_validate(cfg.model_dump()) == cfg

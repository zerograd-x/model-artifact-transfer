from pathlib import Path

from download_model_pipeline.task import download_model


def test_download_model_uses_hdfs_tail_for_staging_name():
    observed = {}

    def fake_snapshot_download(*, repo_id, local_dir):
        observed["repo_id"] = repo_id
        observed["local_dir"] = local_dir
        Path(local_dir, "config.json").write_text("{}")
        return local_dir

    def fake_upload_tree(src, dest, *, max_workers):
        observed["src"] = src
        observed["dest"] = dest
        observed["max_workers"] = max_workers
        assert Path(src, "config.json").exists()

    result = download_model(
        {
            "hf_repo_id": "Qwen/Qwen3-4B",
            "hdfs_path": "hdfs://example-cluster/models/Some_Arbitrary_Name_20260824",
            "upload_parallelism": 7,
        },
        snapshot_download_fn=fake_snapshot_download,
        upload_tree_fn=fake_upload_tree,
    )

    assert observed["repo_id"] == "Qwen/Qwen3-4B"
    assert Path(observed["local_dir"]).name == "Some_Arbitrary_Name_20260824"
    assert observed["dest"] == "hdfs://example-cluster/models/Some_Arbitrary_Name_20260824"
    assert observed["max_workers"] == 7
    assert result == {
        "hdfs_path": "hdfs://example-cluster/models/Some_Arbitrary_Name_20260824",
        "hf_repo_id": "Qwen/Qwen3-4B",
    }

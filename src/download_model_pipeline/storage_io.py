"""Backward-compatible HDFS helpers.

New code should import from :mod:`model_artifact_transfer.hdfs_io`.
"""

from model_artifact_transfer.hdfs_io import (
    HdfsError,
    _hdfs_put_file,
    _remote_join,
    _run_hdfs,
    hdfs_overwrite_enabled,
    hdfs_upload_tree,
)

_hdfs_overwrite_enabled = hdfs_overwrite_enabled

__all__ = [
    "HdfsError",
    "_hdfs_overwrite_enabled",
    "_hdfs_put_file",
    "_remote_join",
    "_run_hdfs",
    "hdfs_upload_tree",
]

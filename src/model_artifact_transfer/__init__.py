"""Portable model-artifact transfer primitives."""

from .core import ArtifactDestination, ArtifactSource, transfer_artifact
from .hdfs import HdfsDestination
from .huggingface import HuggingFaceSource

__all__ = [
    "ArtifactDestination",
    "ArtifactSource",
    "HdfsDestination",
    "HuggingFaceSource",
    "transfer_artifact",
]

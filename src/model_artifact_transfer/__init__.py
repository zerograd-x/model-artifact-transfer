"""Portable model-artifact transfer primitives."""

from .core import ArtifactDestination, ArtifactSource, transfer_artifact
from .huggingface import HuggingFaceSource
from .s3 import S3Destination

__all__ = [
    "ArtifactDestination",
    "ArtifactSource",
    "HuggingFaceSource",
    "S3Destination",
    "transfer_artifact",
]

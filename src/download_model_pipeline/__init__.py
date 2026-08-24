"""Hugging Face -> HDFS model ingestion pipeline."""

from .config import DownloadModelConfig
from .task import download_model

__all__ = ["DownloadModelConfig", "download_model"]

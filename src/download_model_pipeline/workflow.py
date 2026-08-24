from __future__ import annotations

from typing import Any

from .task import download_model


def main(download_config: dict[str, Any]) -> dict[str, str]:
    """Run the single model download task."""
    return download_model(download_config)

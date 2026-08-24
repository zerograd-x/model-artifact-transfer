from pydantic import BaseModel, ConfigDict, Field


class DownloadModelConfig(BaseModel):
    """Configuration for one model download-and-upload run."""

    model_config = ConfigDict(extra="forbid")

    hf_repo_id: str
    hdfs_path: str
    upload_parallelism: int = Field(default=16, ge=1)

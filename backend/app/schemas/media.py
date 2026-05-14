from pydantic import BaseModel, Field


class MediaFileInput(BaseModel):
    name: str
    type: str
    size: int


class MediaGenerateRequest(BaseModel):
    mode: str = Field(pattern="^(prompt|media|link)$")
    prompt: str | None = None
    source_link: str | None = None
    uploads: list[MediaFileInput] = Field(default_factory=list)
    duration: int = 10
    style: str = "cinematic"
    model: str = "axi-video-v1"
    project_name: str = "Novo video"


class MediaGenerateResponse(BaseModel):
    job_id: int
    project_id: int
    status: str


class MediaJobStatusResponse(BaseModel):
    id: int
    status: str
    progress: int
    result_url: str | None = None
    project_id: int | None = None


class MediaExportRequest(BaseModel):
    project_id: int
    resolution: str = Field(pattern="^(720p|1080p|UHD)$")
    format: str = Field(default="mp4", pattern="^mp4$")


class MediaExportResponse(BaseModel):
    job_id: int
    status: str
    download_url: str


class MediaProjectCreate(BaseModel):
    name: str
    timeline_data: dict = Field(default_factory=dict)
    thumbnail: str | None = None
    duration: int = 0


class MediaProjectUpdate(BaseModel):
    name: str | None = None
    timeline_data: dict | None = None
    thumbnail: str | None = None
    duration: int | None = None


class MediaProjectRead(BaseModel):
    id: int
    user_id: int
    name: str
    timeline_data: dict
    thumbnail: str | None = None
    duration: int
    created_at: str
    updated_at: str


class MediaProjectDuplicateResponse(BaseModel):
    id: int

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class StudioProjectCreate(BaseModel):
    project_type: str
    title: str
    metadata: dict[str, Any] = Field(default_factory=dict)
    canvas_data: dict[str, Any] = Field(default_factory=dict)
    layers: list[dict[str, Any]] = Field(default_factory=list)
    timeline_data: dict[str, Any] = Field(default_factory=dict)
    export_settings: dict[str, Any] = Field(default_factory=dict)
    preview_thumbnail_url: str | None = None


class StudioProjectUpdate(BaseModel):
    title: str | None = None
    status: str | None = None
    metadata: dict[str, Any] | None = None
    canvas_data: dict[str, Any] | None = None
    layers: list[dict[str, Any]] | None = None
    timeline_data: dict[str, Any] | None = None
    export_settings: dict[str, Any] | None = None
    preview_thumbnail_url: str | None = None


class StudioProjectRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    project_type: str
    title: str
    status: str
    metadata: dict[str, Any]
    canvas_data: dict[str, Any]
    layers: list[dict[str, Any]]
    timeline_data: dict[str, Any]
    export_settings: dict[str, Any]
    preview_thumbnail_url: str | None = None
    created_at: datetime
    updated_at: datetime


class StudioVersionCreate(BaseModel):
    label: str
    canvas_data: dict[str, Any] = Field(default_factory=dict)
    layers: list[dict[str, Any]] = Field(default_factory=list)
    timeline_data: dict[str, Any] = Field(default_factory=dict)


class StudioVersionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    project_id: int
    label: str
    canvas_data: dict[str, Any]
    layers: list[dict[str, Any]]
    timeline_data: dict[str, Any]
    created_at: datetime


class StudioGenerateRequest(BaseModel):
    project_id: int | None = None
    prompt: str
    objective: str | None = None
    audience: str | None = None
    tone: str | None = None
    offer: str | None = None
    cta: str | None = None
    style: str | None = None
    options: dict[str, Any] = Field(default_factory=dict)


class StudioGenerateResponse(BaseModel):
    generation_id: int
    status: str
    result: dict[str, Any]


class StudioImageRequest(BaseModel):
    project_id: int | None = None
    asset_url: str | None = None
    options: dict[str, Any] = Field(default_factory=dict)


class StudioVideoRequest(BaseModel):
    project_id: int | None = None
    prompt: str
    options: dict[str, Any] = Field(default_factory=dict)


class StudioAssetRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    project_id: int | None
    asset_type: str
    name: str
    file_url: str
    metadata: dict[str, Any]
    created_at: datetime


class StudioAssetDeleteResponse(BaseModel):
    deleted: bool


class StudioTemplateRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int | None
    name: str
    category: str
    style_tag: str | None
    template_data: dict[str, Any]
    preview_url: str | None
    is_public: bool
    created_at: datetime


class StudioTemplateApplyRequest(BaseModel):
    template_id: int
    project_id: int


class StudioTemplateApplyResponse(BaseModel):
    applied: bool
    project: StudioProjectRead


class StudioExportRequest(BaseModel):
    export_type: str = Field(pattern="^(png|jpg|webp|mp4|pdf|zip)$")
    options: dict[str, Any] = Field(default_factory=dict)


class StudioExportRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    project_id: int
    export_type: str
    file_url: str
    status: str
    metadata: dict[str, Any]
    created_at: datetime

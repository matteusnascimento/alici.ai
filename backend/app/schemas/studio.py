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


class StudioRecentProjectItem(BaseModel):
    id: int
    title: str
    project_type: str
    status: str
    updated_at: datetime
    thumbnail_url: str | None = None


class StudioRecentExportItem(BaseModel):
    id: int
    project_id: int
    project_title: str
    file_name: str
    export_type: str
    source: str
    file_url: str
    created_at: datetime


class StudioBrandSummary(BaseModel):
    logos_count: int
    templates_count: int
    palettes_count: int
    assets_count: int


class StudioOverviewResponse(BaseModel):
    recent_projects: list[StudioRecentProjectItem]
    recent_exports: list[StudioRecentExportItem]
    brand_summary: StudioBrandSummary
    suggested_actions: list[dict[str, str]]


class StudioCreativeCreateRequest(BaseModel):
    title: str | None = None
    prompt: str | None = None
    template_id: int | None = None
    upload_urls: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class StudioAdCreateRequest(BaseModel):
    title: str | None = None
    product: str
    offer: str
    audience: str
    channel: str
    prompt: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class StudioCaptionGenerateRequest(BaseModel):
    project_id: int | None = None
    campaign_context: str
    channel: str = "instagram"
    tone: str = "conversacional"
    include_cta: bool = True
    include_hashtags: bool = True
    variations: int = Field(default=3, ge=1, le=6)


class StudioTextGenerateRequest(BaseModel):
    project_id: int | None = None
    campaign_context: str
    channel: str = "instagram"
    tone: str = "persuasivo"
    variations: int = Field(default=3, ge=1, le=6)


class StudioAICreativeRequest(BaseModel):
    project_id: int | None = None
    action: str = "Campanha"
    briefing: str


class StudioPhotoEditRequest(BaseModel):
    project_id: int | None = None
    asset_url: str | None = None
    adjustments: dict[str, Any] = Field(default_factory=dict)
    actions: list[str] = Field(default_factory=list)


class StudioBackgroundRemoveRequest(BaseModel):
    project_id: int | None = None
    asset_url: str | None = None
    options: dict[str, Any] = Field(default_factory=dict)


class StudioToolActionResponse(BaseModel):
    project: StudioProjectRead
    generation: StudioGenerateResponse | None = None
    message: str

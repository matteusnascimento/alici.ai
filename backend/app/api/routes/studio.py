import json

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.studio import (
    StudioAdCreateRequest,
    StudioAssetDeleteResponse,
    StudioAssetRead,
    StudioBackgroundRemoveRequest,
    StudioBrandSummary,
    StudioCaptionGenerateRequest,
    StudioCreativeCreateRequest,
    StudioExportRead,
    StudioExportRequest,
    StudioGenerateRequest,
    StudioGenerateResponse,
    StudioImageRequest,
    StudioOverviewResponse,
    StudioPhotoEditRequest,
    StudioProjectCreate,
    StudioProjectRead,
    StudioProjectUpdate,
    StudioRecentExportItem,
    StudioRecentProjectItem,
    StudioTextGenerateRequest,
    StudioTemplateApplyRequest,
    StudioTemplateApplyResponse,
    StudioTemplateRead,
    StudioToolActionResponse,
    StudioVersionCreate,
    StudioVersionRead,
    StudioVideoRequest,
    StudioAICreativeRequest,
)
from app.services.ai_service import AIServiceError
from app.services.brand_library_service import BrandLibraryService
from app.services.creative_generation_service import CreativeGenerationService
from app.services.media_processing_service import MediaProcessingService
from app.services.studio_asset_service import StudioAssetService
from app.services.studio_export_service import StudioExportService
from app.services.studio_generation_service import StudioGenerationService
from app.services.studio_image_service import StudioImageService
from app.services.studio_project_service import StudioProjectService
from app.services.studio_service import StudioService
from app.services.studio_template_service import StudioTemplateService
from app.services.studio_video_service import StudioVideoService

router = APIRouter(prefix="/studio", tags=["studio"])


def _raise_ai_http_error(exc: AIServiceError) -> None:
    raise HTTPException(status_code=exc.status_code, detail=exc.user_message) from exc


def _project_read(project) -> StudioProjectRead:
    return StudioProjectRead(
        id=project.id,
        user_id=project.user_id,
        project_type=project.project_type,
        title=project.title,
        status=project.status,
        metadata=json.loads(project.metadata_json or "{}"),
        canvas_data=json.loads(project.canvas_data_json or "{}"),
        layers=json.loads(project.layers_json or "[]"),
        timeline_data=json.loads(project.timeline_data_json or "{}"),
        export_settings=json.loads(project.export_settings_json or "{}"),
        preview_thumbnail_url=project.preview_thumbnail_url,
        created_at=project.created_at,
        updated_at=project.updated_at,
    )


def _version_read(version) -> StudioVersionRead:
    return StudioVersionRead(
        id=version.id,
        user_id=version.user_id,
        project_id=version.project_id,
        label=version.label,
        canvas_data=json.loads(version.canvas_data_json or "{}"),
        layers=json.loads(version.layers_json or "[]"),
        timeline_data=json.loads(version.timeline_data_json or "{}"),
        created_at=version.created_at,
    )


def _asset_read(asset) -> StudioAssetRead:
    return StudioAssetRead(
        id=asset.id,
        user_id=asset.user_id,
        project_id=asset.project_id,
        asset_type=asset.asset_type,
        name=asset.name,
        file_url=asset.file_url,
        metadata=json.loads(asset.metadata_json or "{}"),
        created_at=asset.created_at,
    )


def _template_read(item) -> StudioTemplateRead:
    return StudioTemplateRead(
        id=item.id,
        user_id=item.user_id,
        name=item.name,
        category=item.category,
        style_tag=item.style_tag,
        template_data=json.loads(item.template_data_json or "{}"),
        preview_url=item.preview_url,
        is_public=item.is_public,
        created_at=item.created_at,
    )


def _export_read(item) -> StudioExportRead:
    return StudioExportRead(
        id=item.id,
        user_id=item.user_id,
        project_id=item.project_id,
        export_type=item.export_type,
        file_url=item.file_url,
        status=item.status,
        metadata=json.loads(item.metadata_json or "{}"),
        created_at=item.created_at,
    )


@router.get("/projects", response_model=list[StudioProjectRead])
def list_projects(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> list[StudioProjectRead]:
    service = StudioProjectService(db)
    return [_project_read(item) for item in service.list_projects(current_user)]


@router.get("/overview", response_model=StudioOverviewResponse)
def get_studio_overview(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> StudioOverviewResponse:
    service = StudioService(db)
    return service.get_overview(current_user)


@router.get("/projects/recent", response_model=list[StudioRecentProjectItem])
def list_recent_projects(
    limit: int = Query(default=6, ge=1, le=20),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[StudioRecentProjectItem]:
    service = StudioService(db)
    return service.list_recent_projects(current_user, limit=limit)


@router.get("/exports/recent", response_model=list[StudioRecentExportItem])
def list_recent_exports(
    limit: int = Query(default=6, ge=1, le=20),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[StudioRecentExportItem]:
    service = StudioService(db)
    return service.list_recent_exports(current_user, limit=limit)


@router.get("/brand/summary", response_model=StudioBrandSummary)
def get_brand_summary(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> StudioBrandSummary:
    service = BrandLibraryService(db)
    return service.summary(current_user)


@router.post("/projects", response_model=StudioProjectRead)
def create_project(
    payload: StudioProjectCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> StudioProjectRead:
    service = StudioProjectService(db)
    return _project_read(service.create_project(current_user, payload))


@router.get("/projects/{project_id}", response_model=StudioProjectRead)
def get_project(project_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> StudioProjectRead:
    service = StudioProjectService(db)
    return _project_read(service.get_project(current_user, project_id))


@router.patch("/projects/{project_id}", response_model=StudioProjectRead)
def update_project(
    project_id: int,
    payload: StudioProjectUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> StudioProjectRead:
    service = StudioProjectService(db)
    return _project_read(service.update_project(current_user, project_id, payload))


@router.post("/projects/{project_id}/save", response_model=StudioProjectRead)
def save_project(
    project_id: int,
    payload: StudioProjectUpdate | None = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> StudioProjectRead:
    service = StudioProjectService(db)
    return _project_read(service.save_project(current_user, project_id, payload))


@router.post("/projects/{project_id}/duplicate", response_model=StudioProjectRead)
def duplicate_project(project_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> StudioProjectRead:
    service = StudioProjectService(db)
    return _project_read(service.duplicate_project(current_user, project_id))


@router.post("/projects/{project_id}/versions", response_model=StudioVersionRead)
def create_version(
    project_id: int,
    payload: StudioVersionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> StudioVersionRead:
    service = StudioProjectService(db)
    return _version_read(service.create_version(current_user, project_id, payload))


@router.get("/projects/{project_id}/versions", response_model=list[StudioVersionRead])
def list_versions(project_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> list[StudioVersionRead]:
    service = StudioProjectService(db)
    return [_version_read(item) for item in service.list_versions(current_user, project_id)]


@router.post("/projects/{project_id}/export", response_model=StudioExportRead)
def export_project(
    project_id: int,
    payload: StudioExportRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> StudioExportRead:
    service = StudioExportService(db)
    return _export_read(service.create_export(current_user, project_id, payload.export_type, payload.options))


@router.post("/generate/poster", response_model=StudioGenerateResponse)
def generate_poster(payload: StudioGenerateRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> StudioGenerateResponse:
    generation_service = StudioGenerationService(db)
    try:
        result = generation_service.generate_poster_variations(payload.prompt, {**payload.options, "style": payload.style})
    except AIServiceError as exc:
        _raise_ai_http_error(exc)
    item = generation_service.create_generation(
        user_id=current_user.id,
        project_id=payload.project_id,
        generation_type="poster",
        prompt=payload.prompt,
        input_payload=payload.model_dump(),
        result_payload=result,
    )
    return StudioGenerateResponse(generation_id=item.id, status=item.status, result=result)


@router.post("/generate/story", response_model=StudioGenerateResponse)
def generate_story(payload: StudioGenerateRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> StudioGenerateResponse:
    generation_service = StudioGenerationService(db)
    try:
        result = generation_service.generate_poster_variations(payload.prompt, {**payload.options, "style": "story"})
    except AIServiceError as exc:
        _raise_ai_http_error(exc)
    item = generation_service.create_generation(
        user_id=current_user.id,
        project_id=payload.project_id,
        generation_type="story",
        prompt=payload.prompt,
        input_payload=payload.model_dump(),
        result_payload=result,
    )
    return StudioGenerateResponse(generation_id=item.id, status=item.status, result=result)


@router.post("/generate/banner", response_model=StudioGenerateResponse)
def generate_banner(payload: StudioGenerateRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> StudioGenerateResponse:
    generation_service = StudioGenerationService(db)
    try:
        result = generation_service.generate_poster_variations(payload.prompt, {**payload.options, "style": "banner"})
    except AIServiceError as exc:
        _raise_ai_http_error(exc)
    item = generation_service.create_generation(
        user_id=current_user.id,
        project_id=payload.project_id,
        generation_type="banner",
        prompt=payload.prompt,
        input_payload=payload.model_dump(),
        result_payload=result,
    )
    return StudioGenerateResponse(generation_id=item.id, status=item.status, result=result)


@router.post("/generate/ad-copy", response_model=StudioGenerateResponse)
def generate_ad_copy(payload: StudioGenerateRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> StudioGenerateResponse:
    generation_service = StudioGenerationService(db)
    try:
        result = generation_service.generate_copy(payload.prompt, "ad-copy")
    except AIServiceError as exc:
        _raise_ai_http_error(exc)
    item = generation_service.create_generation(
        user_id=current_user.id,
        project_id=payload.project_id,
        generation_type="ad-copy",
        prompt=payload.prompt,
        input_payload=payload.model_dump(),
        result_payload=result,
    )
    return StudioGenerateResponse(generation_id=item.id, status=item.status, result=result)


@router.post("/generate/headline", response_model=StudioGenerateResponse)
def generate_headline(payload: StudioGenerateRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> StudioGenerateResponse:
    generation_service = StudioGenerationService(db)
    try:
        result = generation_service.generate_copy(payload.prompt, "headline")
    except AIServiceError as exc:
        _raise_ai_http_error(exc)
    item = generation_service.create_generation(
        user_id=current_user.id,
        project_id=payload.project_id,
        generation_type="headline",
        prompt=payload.prompt,
        input_payload=payload.model_dump(),
        result_payload=result,
    )
    return StudioGenerateResponse(generation_id=item.id, status=item.status, result=result)


@router.post("/generate/variations", response_model=StudioGenerateResponse)
def generate_variations(payload: StudioGenerateRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> StudioGenerateResponse:
    generation_service = StudioGenerationService(db)
    try:
        result = generation_service.generate_poster_variations(payload.prompt, payload.options)
    except AIServiceError as exc:
        _raise_ai_http_error(exc)
    item = generation_service.create_generation(
        user_id=current_user.id,
        project_id=payload.project_id,
        generation_type="variations",
        prompt=payload.prompt,
        input_payload=payload.model_dump(),
        result_payload=result,
    )
    return StudioGenerateResponse(generation_id=item.id, status=item.status, result=result)


@router.post("/generate/brand-style", response_model=StudioGenerateResponse)
def generate_brand_style(payload: StudioGenerateRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> StudioGenerateResponse:
    generation_service = StudioGenerationService(db)
    try:
        result = generation_service.generate_brand_style(payload.prompt)
    except AIServiceError as exc:
        _raise_ai_http_error(exc)
    item = generation_service.create_generation(
        user_id=current_user.id,
        project_id=payload.project_id,
        generation_type="brand-style",
        prompt=payload.prompt,
        input_payload=payload.model_dump(),
        result_payload=result,
    )
    return StudioGenerateResponse(generation_id=item.id, status=item.status, result=result)


@router.post("/image/remove-background", response_model=StudioGenerateResponse)
def remove_background(payload: StudioImageRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> StudioGenerateResponse:
    generation_service = StudioGenerationService(db)
    result = StudioImageService.remove_background(payload.asset_url, payload.options)
    item = generation_service.create_generation(
        user_id=current_user.id,
        project_id=payload.project_id,
        generation_type="image-remove-background",
        prompt="remove-background",
        input_payload=payload.model_dump(),
        result_payload=result,
    )
    return StudioGenerateResponse(generation_id=item.id, status=item.status, result=result)


@router.post("/image/retouch", response_model=StudioGenerateResponse)
def image_retouch(payload: StudioImageRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> StudioGenerateResponse:
    generation_service = StudioGenerationService(db)
    result = StudioImageService.retouch(payload.asset_url, payload.options)
    item = generation_service.create_generation(
        user_id=current_user.id,
        project_id=payload.project_id,
        generation_type="image-retouch",
        prompt="retouch",
        input_payload=payload.model_dump(),
        result_payload=result,
    )
    return StudioGenerateResponse(generation_id=item.id, status=item.status, result=result)


@router.post("/image/enhance", response_model=StudioGenerateResponse)
def image_enhance(payload: StudioImageRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> StudioGenerateResponse:
    generation_service = StudioGenerationService(db)
    result = StudioImageService.enhance(payload.asset_url, payload.options)
    item = generation_service.create_generation(
        user_id=current_user.id,
        project_id=payload.project_id,
        generation_type="image-enhance",
        prompt="enhance",
        input_payload=payload.model_dump(),
        result_payload=result,
    )
    return StudioGenerateResponse(generation_id=item.id, status=item.status, result=result)


@router.post("/image/resize", response_model=StudioGenerateResponse)
def image_resize(payload: StudioImageRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> StudioGenerateResponse:
    generation_service = StudioGenerationService(db)
    result = StudioImageService.resize(payload.asset_url, payload.options)
    item = generation_service.create_generation(
        user_id=current_user.id,
        project_id=payload.project_id,
        generation_type="image-resize",
        prompt="resize",
        input_payload=payload.model_dump(),
        result_payload=result,
    )
    return StudioGenerateResponse(generation_id=item.id, status=item.status, result=result)


@router.post("/image/filter", response_model=StudioGenerateResponse)
def image_filter(payload: StudioImageRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> StudioGenerateResponse:
    generation_service = StudioGenerationService(db)
    result = StudioImageService.filter_image(payload.asset_url, payload.options)
    item = generation_service.create_generation(
        user_id=current_user.id,
        project_id=payload.project_id,
        generation_type="image-filter",
        prompt="filter",
        input_payload=payload.model_dump(),
        result_payload=result,
    )
    return StudioGenerateResponse(generation_id=item.id, status=item.status, result=result)


@router.post("/image/upscale", response_model=StudioGenerateResponse)
def image_upscale(payload: StudioImageRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> StudioGenerateResponse:
    generation_service = StudioGenerationService(db)
    result = StudioImageService.upscale(payload.asset_url, payload.options)
    item = generation_service.create_generation(
        user_id=current_user.id,
        project_id=payload.project_id,
        generation_type="image-upscale",
        prompt="upscale",
        input_payload=payload.model_dump(),
        result_payload=result,
    )
    return StudioGenerateResponse(generation_id=item.id, status=item.status, result=result)


@router.post("/video/generate", response_model=StudioGenerateResponse)
def video_generate(payload: StudioVideoRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> StudioGenerateResponse:
    generation_service = StudioGenerationService(db)
    result = StudioVideoService.generate(payload.prompt, payload.options)
    item = generation_service.create_generation(
        user_id=current_user.id,
        project_id=payload.project_id,
        generation_type="video-generate",
        prompt=payload.prompt,
        input_payload=payload.model_dump(),
        result_payload=result,
    )
    return StudioGenerateResponse(generation_id=item.id, status=item.status, result=result)


@router.post("/video/captions", response_model=StudioGenerateResponse)
def video_captions(payload: StudioVideoRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> StudioGenerateResponse:
    generation_service = StudioGenerationService(db)
    try:
        result = StudioVideoService.captions(payload.prompt, payload.options)
    except AIServiceError as exc:
        _raise_ai_http_error(exc)
    item = generation_service.create_generation(
        user_id=current_user.id,
        project_id=payload.project_id,
        generation_type="video-captions",
        prompt=payload.prompt,
        input_payload=payload.model_dump(),
        result_payload=result,
    )
    return StudioGenerateResponse(generation_id=item.id, status=item.status, result=result)


@router.post("/video/cut", response_model=StudioGenerateResponse)
def video_cut(payload: StudioVideoRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> StudioGenerateResponse:
    generation_service = StudioGenerationService(db)
    result = StudioVideoService.cut(payload.prompt, payload.options)
    item = generation_service.create_generation(
        user_id=current_user.id,
        project_id=payload.project_id,
        generation_type="video-cut",
        prompt=payload.prompt,
        input_payload=payload.model_dump(),
        result_payload=result,
    )
    return StudioGenerateResponse(generation_id=item.id, status=item.status, result=result)


@router.post("/video/voiceover", response_model=StudioGenerateResponse)
def video_voiceover(payload: StudioVideoRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> StudioGenerateResponse:
    generation_service = StudioGenerationService(db)
    try:
        result = StudioVideoService.voiceover(payload.prompt, payload.options)
    except AIServiceError as exc:
        _raise_ai_http_error(exc)
    item = generation_service.create_generation(
        user_id=current_user.id,
        project_id=payload.project_id,
        generation_type="video-voiceover",
        prompt=payload.prompt,
        input_payload=payload.model_dump(),
        result_payload=result,
    )
    return StudioGenerateResponse(generation_id=item.id, status=item.status, result=result)


@router.post("/video/export", response_model=StudioGenerateResponse)
def video_export(payload: StudioVideoRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> StudioGenerateResponse:
    generation_service = StudioGenerationService(db)
    result = StudioVideoService.export(payload.prompt, payload.options)
    item = generation_service.create_generation(
        user_id=current_user.id,
        project_id=payload.project_id,
        generation_type="video-export",
        prompt=payload.prompt,
        input_payload=payload.model_dump(),
        result_payload=result,
    )
    return StudioGenerateResponse(generation_id=item.id, status=item.status, result=result)


@router.post("/video/thumbnail", response_model=StudioGenerateResponse)
def video_thumbnail(payload: StudioVideoRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> StudioGenerateResponse:
    generation_service = StudioGenerationService(db)
    result = StudioVideoService.thumbnail(payload.prompt, payload.options)
    item = generation_service.create_generation(
        user_id=current_user.id,
        project_id=payload.project_id,
        generation_type="video-thumbnail",
        prompt=payload.prompt,
        input_payload=payload.model_dump(),
        result_payload=result,
    )
    return StudioGenerateResponse(generation_id=item.id, status=item.status, result=result)


@router.post("/assets/upload", response_model=StudioAssetRead)
async def upload_asset(
    file: UploadFile = File(...),
    project_id: int | None = Query(default=None),
    asset_type: str = Query(default="image"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> StudioAssetRead:
    if not file.filename:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid file")
    service = StudioAssetService(db)
    asset = service.create_asset(
        current_user,
        name=file.filename,
        asset_type=asset_type,
        project_id=project_id,
        metadata={"content_type": file.content_type},
    )
    return _asset_read(asset)


@router.get("/assets/list", response_model=list[StudioAssetRead])
def list_assets(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> list[StudioAssetRead]:
    service = StudioAssetService(db)
    return [_asset_read(item) for item in service.list_assets(current_user)]


@router.delete("/assets/delete/{asset_id}", response_model=StudioAssetDeleteResponse)
def delete_asset(asset_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> StudioAssetDeleteResponse:
    service = StudioAssetService(db)
    deleted = service.delete_asset(current_user, asset_id)
    return StudioAssetDeleteResponse(deleted=deleted)


@router.get("/templates/list", response_model=list[StudioTemplateRead])
def list_templates(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> list[StudioTemplateRead]:
    service = StudioTemplateService(db)
    return [_template_read(item) for item in service.list_templates(current_user)]


@router.post("/templates/apply", response_model=StudioTemplateApplyResponse)
def apply_template(
    payload: StudioTemplateApplyRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> StudioTemplateApplyResponse:
    service = StudioTemplateService(db)
    project = service.apply_template(current_user, payload.template_id, payload.project_id)
    return StudioTemplateApplyResponse(applied=True, project=_project_read(project))


@router.get("/exports", response_model=list[StudioExportRead])
def list_exports(
    project_id: int | None = Query(default=None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[StudioExportRead]:
    service = StudioExportService(db)
    return [_export_read(item) for item in service.list_exports(current_user, project_id)]


@router.post("/poster/create", response_model=StudioToolActionResponse)
def create_poster_workspace(
    payload: StudioCreativeCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> StudioToolActionResponse:
    service = CreativeGenerationService(db)
    try:
        return service.create_poster(current_user, payload)
    except AIServiceError as exc:
        _raise_ai_http_error(exc)


@router.post("/story/create", response_model=StudioToolActionResponse)
def create_story_workspace(
    payload: StudioCreativeCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> StudioToolActionResponse:
    service = CreativeGenerationService(db)
    try:
        return service.create_story(current_user, payload)
    except AIServiceError as exc:
        _raise_ai_http_error(exc)


@router.post("/ad/create", response_model=StudioToolActionResponse)
def create_ad_workspace(
    payload: StudioAdCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> StudioToolActionResponse:
    service = CreativeGenerationService(db)
    try:
        return service.create_ad(current_user, payload)
    except AIServiceError as exc:
        _raise_ai_http_error(exc)


@router.post("/ad-builder/create", response_model=StudioToolActionResponse)
def create_ad_builder_workspace(
    payload: StudioAdCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> StudioToolActionResponse:
    service = CreativeGenerationService(db)
    try:
        return service.create_ad(current_user, payload)
    except AIServiceError as exc:
        _raise_ai_http_error(exc)


@router.post("/video/create", response_model=StudioToolActionResponse)
def create_video_workspace(
    payload: StudioCreativeCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> StudioToolActionResponse:
    service = CreativeGenerationService(db)
    return service.create_video(current_user, payload)


@router.post("/video-editor/create", response_model=StudioToolActionResponse)
def create_video_editor_workspace(
    payload: StudioCreativeCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> StudioToolActionResponse:
    service = CreativeGenerationService(db)
    return service.create_video(current_user, payload)


@router.post("/photo/edit", response_model=StudioToolActionResponse)
def edit_photo_workspace(
    payload: StudioPhotoEditRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> StudioToolActionResponse:
    service = MediaProcessingService(db)
    return service.edit_photo(current_user, payload)


@router.post("/photo-editor/save", response_model=StudioToolActionResponse)
def save_photo_editor_workspace(
    payload: StudioPhotoEditRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> StudioToolActionResponse:
    service = MediaProcessingService(db)
    return service.edit_photo(current_user, payload)


@router.post("/background-remove", response_model=StudioToolActionResponse)
def background_remove_workspace(
    payload: StudioBackgroundRemoveRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> StudioToolActionResponse:
    service = MediaProcessingService(db)
    return service.remove_background(current_user, payload)


@router.post("/background-remove/process", response_model=StudioToolActionResponse)
def background_remove_process(
    payload: StudioBackgroundRemoveRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> StudioToolActionResponse:
    service = MediaProcessingService(db)
    return service.remove_background(current_user, payload)


@router.post("/caption/generate", response_model=StudioGenerateResponse)
def caption_generate(
    payload: StudioCaptionGenerateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> StudioGenerateResponse:
    service = CreativeGenerationService(db)
    try:
        return service.generate_caption(
            current_user,
            project_id=payload.project_id,
            campaign_context=payload.campaign_context,
            channel=payload.channel,
            tone=payload.tone,
            include_cta=payload.include_cta,
            include_hashtags=payload.include_hashtags,
            variations=payload.variations,
        )
    except AIServiceError as exc:
        _raise_ai_http_error(exc)


@router.post("/cta/generate", response_model=StudioGenerateResponse)
def cta_generate(
    payload: StudioTextGenerateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> StudioGenerateResponse:
    service = CreativeGenerationService(db)
    try:
        return service.generate_cta(
            current_user,
            project_id=payload.project_id,
            campaign_context=payload.campaign_context,
            channel=payload.channel,
            tone=payload.tone,
            variations=payload.variations,
        )
    except AIServiceError as exc:
        _raise_ai_http_error(exc)


@router.post("/copy/generate", response_model=StudioGenerateResponse)
def copy_generate(
    payload: StudioTextGenerateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> StudioGenerateResponse:
    service = CreativeGenerationService(db)
    try:
        return service.generate_promo_copy(
            current_user,
            project_id=payload.project_id,
            campaign_context=payload.campaign_context,
            channel=payload.channel,
            tone=payload.tone,
            variations=payload.variations,
        )
    except AIServiceError as exc:
        _raise_ai_http_error(exc)


@router.post("/ai-creative/generate", response_model=StudioGenerateResponse)
def ai_creative_generate(
    payload: StudioAICreativeRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> StudioGenerateResponse:
    service = CreativeGenerationService(db)
    try:
        return service.ai_creative_assistant(
            current_user,
            project_id=payload.project_id,
            action=payload.action,
            briefing=payload.briefing,
        )
    except AIServiceError as exc:
        _raise_ai_http_error(exc)

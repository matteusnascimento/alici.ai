from __future__ import annotations

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.studio_asset import StudioAsset
from app.models.studio_template import StudioTemplate
from app.models.user import User
from app.schemas.studio import StudioBrandSummary


class BrandLibraryService:
    def __init__(self, db: Session):
        self.db = db

    def summary(self, user: User) -> StudioBrandSummary:
        logos_count = (
            self.db.query(StudioAsset)
            .filter(StudioAsset.user_id == user.id, StudioAsset.asset_type.in_(["logo", "brand-logo"]))
            .count()
        )
        templates_count = (
            self.db.query(StudioTemplate)
            .filter((StudioTemplate.user_id == user.id) | (StudioTemplate.is_public.is_(True)))
            .count()
        )
        assets_count = self.db.query(StudioAsset).filter(StudioAsset.user_id == user.id).count()

        palettes_count = (
            self.db.query(func.count(StudioAsset.id))
            .filter(StudioAsset.user_id == user.id, StudioAsset.asset_type.in_(["palette", "color-palette"]))
            .scalar()
            or 0
        )

        return StudioBrandSummary(
            logos_count=logos_count,
            templates_count=templates_count,
            palettes_count=int(palettes_count),
            assets_count=assets_count,
        )

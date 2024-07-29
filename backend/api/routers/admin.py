from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from typing import Annotated

from rope.api.auth import verify_user, verify_admin
from rope.api import database
from rope.api.models import (
    BaseSchoolDistrict,
    FullSchoolDistrict,
    BaseMoodleSettings,
    FullMoodleSettings,
)


router = APIRouter(
    tags=["admin"],
)


@router.get("/admin/settings/district")
def get_districts(
    current_user: Annotated[dict, Depends(verify_user)],
    db: Session = Depends(database.get_db),
) -> list[FullSchoolDistrict]:
    active_only = not current_user["is_admin"]
    school_districts = database.get_districts(db, active_only)
    sorted_school_districts = sorted(
        school_districts, key=lambda district: district.name
    )
    return sorted_school_districts


@router.post("/admin/settings/district", dependencies=[Depends(verify_admin)])
def create_district(
    district: BaseSchoolDistrict, db: Session = Depends(database.get_db)
) -> FullSchoolDistrict:
    new_district = database.create_district(db, district)
    return new_district


@router.put("/admin/settings/district/{id}", dependencies=[Depends(verify_admin)])
def update_district(
    district: FullSchoolDistrict, db: Session = Depends(database.get_db)
) -> FullSchoolDistrict:
    updated_district = database.update_district(db, district)
    return updated_district


@router.get("/admin/settings/moodle", dependencies=[Depends(verify_user)])
def get_moodle_settings(
    db: Session = Depends(database.get_db),
) -> list[FullMoodleSettings]:
    moodle_settings = database.get_moodle_settings(db)
    return moodle_settings


@router.post("/admin/settings/moodle", dependencies=[Depends(verify_admin)])
def create_moodle_settings(
    moodle_setting: BaseMoodleSettings, db: Session = Depends(database.get_db)
) -> FullMoodleSettings:
    new_moodle_setting = database.create_moodle_settings(db, moodle_setting)
    return new_moodle_setting


@router.put("/admin/settings/moodle/{id}", dependencies=[Depends(verify_admin)])
def update_moodle_settings(
    moodle_setting: FullMoodleSettings, db: Session = Depends(database.get_db)
) -> FullMoodleSettings:
    updated_moodle_settings = database.update_moodle_settings(db, moodle_setting)
    return updated_moodle_settings

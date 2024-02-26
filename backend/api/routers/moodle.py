from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from typing import Annotated, Optional
import requests

from rope.api.auth import verify_user, verify_manager
from rope.api import database, settings, utils
from rope.db.schema import CourseBuildStatus
from moodlecli.moodle import MoodleClient
from rope.api.models import (
    BaseCourseBuildSettings,
    FullCourseBuildSettings,
    MoodleUser,
)

router = APIRouter(
    prefix="/moodle",
    tags=["moodle"],
)

moodle_client = MoodleClient(
    requests.Session(),
    settings.MOODLE_URL,
    settings.MOODLE_TOKEN,
)


@router.post("/course/build/")
def create_course_build(
    current_user: Annotated[dict, Depends(verify_manager)],
    course_build_settings: BaseCourseBuildSettings,
    db: Session = Depends(database.get_db),
) -> FullCourseBuildSettings:
    academic_year = database.get_moodle_setting_by_name(db, "academic_year")
    academic_year_short = database.get_moodle_setting_by_name(db, "academic_year_short")
    course_category = database.get_moodle_setting_by_name(db, "course_category")
    base_course_id = database.get_moodle_setting_by_name(db, "base_course_id")
    if any(
        setting is None
        for setting in [
            academic_year,
            academic_year_short,
            course_category,
            base_course_id,
        ]
    ):
        raise Exception("One or more expected Moodle settings is not set.")
    instructor_firstname = course_build_settings.instructor_firstname
    instructor_lastname = course_build_settings.instructor_lastname
    instructor_email = course_build_settings.instructor_email
    course_name = utils.create_course_name(
        instructor_firstname,
        instructor_lastname,
        academic_year,
    )
    maybe_course_shortname = utils.create_course_shortname(
        instructor_firstname, instructor_lastname, academic_year_short
    )
    nonce = 1
    while not utils.check_course_shortname_uniqueness(
        db, moodle_client, maybe_course_shortname
    ):
        maybe_course_shortname = utils.create_course_shortname(
            instructor_firstname, instructor_lastname, academic_year_short, nonce
        )
        nonce += 1
    user_db = database.get_user_by_email(db, current_user["email"])
    school_district_name = course_build_settings.school_district
    school_district = database.get_district_by_name(db, school_district_name)
    school_district_id = school_district.id
    creator = user_db.id
    status = CourseBuildStatus.CREATED.value
    database.create_course_build(
        db,
        instructor_firstname,
        instructor_lastname,
        instructor_email,
        school_district_id,
        academic_year,
        academic_year_short,
        course_category,
        base_course_id,
        course_name,
        maybe_course_shortname,
        status,
        creator,
    )
    return {
        "instructor_firstname": instructor_firstname,
        "instructor_lastname": instructor_lastname,
        "instructor_email": instructor_email,
        "school_district": school_district_name,
        "academic_year": academic_year,
        "academic_year_short": academic_year_short,
        "course_name": course_name,
        "course_shortname": maybe_course_shortname,
        "creator": current_user["email"],
        "status": status,
    }


@router.get("/user/", dependencies=[Depends(verify_user)])
def get_moodle_user(email: str = "") -> Optional[MoodleUser]:
    user_data = moodle_client.get_user_by_email(email)
    if not user_data:
        return None
    first_name = user_data.get("firstname")
    last_name = user_data.get("lastname")
    user_email = user_data.get("email")

    return {"first_name": first_name, "last_name": last_name, "email": user_email}

from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from starlette.middleware.sessions import SessionMiddleware
import uuid
import requests
from typing import Annotated, Optional
from rope.api.models import (
    GoogleLoginData,
    BaseUser,
    FullUser,
    BaseSchoolDistrict,
    FullSchoolDistrict,
    BaseMoodleSettings,
    FullMoodleSettings,
    BaseCourseBuildSettings,
    FullCourseBuildSettings,
    MoodleUser,
)
from rope.api.auth import verify_google_token, verify_user, verify_admin, verify_manager
from rope.api import settings, utils, database
from rope.api.sessions import (
    create_session,
    destroy_session,
    get_request_session,
    get_session,
)
from rope.db.schema import CourseBuildStatus
from moodlecli.moodle import MoodleClient

moodle_client = MoodleClient(
    requests.Session(),
    settings.MOODLE_URL,
    settings.MOODLE_TOKEN,
)

app = FastAPI(title="ROPE API", root_path="/api")

app.add_middleware(
    SessionMiddleware,
    secret_key=settings.SESSION_SECRET_KEY,
    https_only=True,
    session_cookie="ROPE.session",
    max_age=60 * 60,  # 1 hour
)


def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/session")
def google_login(
    login_data: GoogleLoginData,
    session=Depends(get_request_session),
    db: Session = Depends(get_db),
):
    token = verify_google_token(login_data.token)
    if not token:
        raise HTTPException(
            status_code=401,
            detail="Invalid token",
        )
    user = database.get_user_by_email(db, token["email"])
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Unauthorized user",
        )
    user_data = {
        "email": user.email,
        "is_manager": user.is_manager,
        "is_admin": user.is_admin,
    }

    new_session_id = str(uuid.uuid4())
    create_session(new_session_id, user_data)
    session["session_id"] = new_session_id
    user_session_data = get_session(session["session_id"])
    return user_session_data


@app.get("/user/current")
def get_current_user(current_user: Annotated[dict, Depends(verify_user)]) -> BaseUser:
    return current_user


@app.delete("/session", dependencies=[Depends(verify_user)])
def delete_session(session=Depends(get_request_session)):
    session_id = session.get("session_id")
    destroy_session(session_id)
    del session["session_id"]


@app.get("/user", dependencies=[Depends(verify_admin)])
def get_users(db: Session = Depends(get_db)) -> list[FullUser]:
    users = database.get_all_users(db)
    return users


@app.post("/user", dependencies=[Depends(verify_admin)])
def create_user(user: BaseUser, db: Session = Depends(get_db)) -> FullUser:
    new_user = database.create_user(db, user)
    return new_user


@app.put("/user/{id}", dependencies=[Depends(verify_admin)])
def update_user(user: FullUser, db: Session = Depends(get_db)) -> FullUser:
    updated_user = database.update_user(db, user)
    return updated_user


@app.delete("/user/{id}", dependencies=[Depends(verify_admin)])
def delete_user(id: int, db: Session = Depends(get_db)):
    row_deleted = database.delete_user(db, id)
    if row_deleted == 0:
        raise HTTPException(
            status_code=404, detail=f"User with the id: {id} does not exist"
        )


@app.get("/admin/settings/district")
def get_districts(
    current_user: Annotated[dict, Depends(verify_user)], db: Session = Depends(get_db)
) -> list[FullSchoolDistrict]:
    active_only = not current_user["is_admin"]
    school_districts = database.get_districts(db, active_only)
    return school_districts


@app.post("/admin/settings/district", dependencies=[Depends(verify_admin)])
def create_district(
    district: BaseSchoolDistrict, db: Session = Depends(get_db)
) -> FullSchoolDistrict:
    new_district = database.create_district(db, district)
    return new_district


@app.put("/admin/settings/district/{id}", dependencies=[Depends(verify_admin)])
def update_district(
    district: FullSchoolDistrict, db: Session = Depends(get_db)
) -> FullSchoolDistrict:
    updated_district = database.update_district(db, district)
    return updated_district


@app.get("/admin/settings/moodle", dependencies=[Depends(verify_user)])
def get_moodle_settings(db: Session = Depends(get_db)) -> list[FullMoodleSettings]:
    moodle_settings = database.get_moodle_settings(db)
    return moodle_settings


@app.post("/admin/settings/moodle", dependencies=[Depends(verify_admin)])
def create_moodle_settings(
    moodle_setting: BaseMoodleSettings, db: Session = Depends(get_db)
) -> FullMoodleSettings:
    new_moodle_setting = database.create_moodle_settings(db, moodle_setting)
    return new_moodle_setting


@app.put("/admin/settings/moodle/{id}", dependencies=[Depends(verify_admin)])
def update_moodle_settings(
    moodle_setting: FullMoodleSettings, db: Session = Depends(get_db)
) -> FullMoodleSettings:
    updated_moodle_settings = database.update_moodle_settings(db, moodle_setting)
    return updated_moodle_settings


@app.post("/moodle/course/build")
def create_course_build(
    current_user: Annotated[dict, Depends(verify_manager)],
    course_build_settings: BaseCourseBuildSettings,
    db: Session = Depends(get_db),
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


@app.get("/moodle/user/", dependencies=[Depends(verify_user)])
def get_moodle_user(email: str = "") -> Optional[MoodleUser]:
    user_data = moodle_client.get_user_by_email(email)
    if not user_data:
        return None
    first_name = user_data.get("firstname")
    last_name = user_data.get("lastname")
    user_email = user_data.get("email")

    return {"first_name": first_name, "last_name": last_name, "email": user_email}

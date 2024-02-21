from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy.exc import NoResultFound
from starlette.middleware.sessions import SessionMiddleware

import uuid
from typing import Annotated

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
)
from rope.api.auth import verify_google_token, verify_user, verify_admin, verify_manager
from rope.api import settings, utils, database
from rope.api.sessions import (
    create_session,
    destroy_session,
    get_request_session,
    get_session,
)
from rope.db.schema import MoodleSetting, CourseBuild, UserAccount


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


@app.post("/moodle/course/build", dependencies=[Depends(verify_manager)])
def create_course_build(
    current_user: Annotated[dict, Depends(verify_user)],
    course_build_settings: BaseCourseBuildSettings,
    db: Session = Depends(get_db),
) -> FullCourseBuildSettings:
    moodle_settings_db = db.query(MoodleSetting).all()
    if len(moodle_settings_db) == 0:
        raise NoResultFound
    moodle_settings = {}
    for setting in moodle_settings_db:
        name = setting.name
        value = setting.value
        moodle_settings[name] = value
    moodle_setting_keys = moodle_settings.keys()
    required_moodle_setting_keys_exist = utils.moodle_settings_key_check(
        moodle_setting_keys
    )
    if not required_moodle_setting_keys_exist:
        raise NoResultFound
    course_name = utils.create_course_name(course_build_settings, moodle_settings)
    course_shortname = utils.create_course_shortname(
        course_build_settings, moodle_settings, False
    )
    course_shortname_exists = (
        db.query(CourseBuild)
        .filter(CourseBuild.course_shortname == course_shortname)
        .first()
    )
    if course_shortname_exists is not None:
        course_shortname = utils.update_course_shortname(
            db,
            course_shortname,
            course_shortname_exists,
            course_build_settings,
            moodle_settings,
        )
    user_db = (
        db.query(UserAccount).filter(UserAccount.email == current_user["email"]).first()
    )
    creator = user_db.id
    status = "CREATED"
    course_build = database.create_course_build(
        db,
        course_build_settings,
        moodle_settings,
        course_name,
        course_shortname,
        status,
        creator,
    )
    return course_build

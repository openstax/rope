from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import NoResultFound, MultipleResultsFound
from rope.db.schema import UserAccount, SchoolDistrict, MoodleSetting, CourseBuild
from rope.api.settings import PG_USER, PG_PASSWORD, PG_SERVER, PG_DB

SQLALCHEMY_DATABASE_URL = f"postgresql://{PG_USER}:{PG_PASSWORD}@{PG_SERVER}/{PG_DB}"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_user_by_email(db: Session, email: str):
    user = db.query(UserAccount).filter(UserAccount.email == email).all()
    if not user:
        return None
    if len(user) > 1:
        raise MultipleResultsFound  # pragma: no cover
    return user[0]


def get_all_users(db: Session):
    users = db.query(UserAccount).all()
    return users


def create_user(db: Session, user):
    new_user = UserAccount(
        email=user.email, is_manager=user.is_manager, is_admin=user.is_admin
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


def update_user(db: Session, user):
    user_db = db.query(UserAccount).filter(UserAccount.id == user.id).first()
    if not user_db:
        raise NoResultFound
    user_db.email = user.email
    user_db.is_manager = user.is_manager
    user_db.is_admin = user.is_admin
    db.commit()
    db.refresh(user_db)
    return user_db


def delete_user(db: Session, id: int):
    rows_deleted = db.query(UserAccount).filter(UserAccount.id == id).delete()
    db.commit()
    return rows_deleted


def get_districts(db: Session, active_only=True):
    if not active_only:
        school_districts = db.query(SchoolDistrict).all()
    else:
        school_districts = db.query(SchoolDistrict).filter(SchoolDistrict.active).all()
    return school_districts


def get_district_by_name(db: Session, school_district_name):
    school_district = (
        db.query(SchoolDistrict)
        .filter(SchoolDistrict.name == school_district_name)
        .first()
    )
    return school_district


def create_district(db: Session, district):
    lower_case_district_name = district.name.lower()
    new_district = SchoolDistrict(name=lower_case_district_name, active=district.active)
    db.add(new_district)
    db.commit()
    db.refresh(new_district)
    return new_district


def update_district(db: Session, district):
    district_db = (
        db.query(SchoolDistrict).filter(SchoolDistrict.id == district.id).first()
    )
    if not district_db:
        raise NoResultFound
    lower_case_district_name = district.name.lower()
    district_db.name = lower_case_district_name
    district_db.active = district.active
    db.commit()
    db.refresh(district_db)
    return district_db


def get_moodle_settings(db: Session):
    moodle_settings = db.query(MoodleSetting).all()
    return moodle_settings


def get_moodle_setting_by_name(db: Session, setting_name):
    moodle_setting = (
        db.query(MoodleSetting).filter(MoodleSetting.name == setting_name).first()
    )
    if not moodle_setting:
        return None

    return moodle_setting.value


def create_moodle_settings(db: Session, moodle_setting):
    lower_case_moodle_setting_name = moodle_setting.name.lower()
    new_moodle_setting = MoodleSetting(
        name=lower_case_moodle_setting_name, value=moodle_setting.value
    )
    db.add(new_moodle_setting)
    db.commit()
    db.refresh(new_moodle_setting)
    return new_moodle_setting


def update_moodle_settings(db: Session, moodle_setting):
    moodle_settings_db = (
        db.query(MoodleSetting).filter(MoodleSetting.id == moodle_setting.id).first()
    )
    if not moodle_settings_db:
        raise NoResultFound
    lower_case_moodle_setting_name = moodle_setting.name.lower()
    moodle_settings_db.name = lower_case_moodle_setting_name
    moodle_settings_db.value = moodle_setting.value
    db.commit()
    db.refresh(moodle_settings_db)
    return moodle_settings_db


def create_course_build(
    db: Session,
    instructor_firstname,
    instructor_lastname,
    instructor_email,
    school_district_id,
    academic_year,
    academic_year_short,
    course_category_id,
    base_course_id,
    course_name,
    course_shortname,
    status,
    creator,
):
    new_course_build = CourseBuild(
        instructor_firstname=instructor_firstname,
        instructor_lastname=instructor_lastname,
        instructor_email=instructor_email,
        course_name=course_name,
        course_shortname=course_shortname,
        course_category_id=course_category_id,
        school_district_id=school_district_id,
        academic_year=academic_year,
        academic_year_short=academic_year_short,
        base_course_id=base_course_id,
        status=status,
        creator_id=creator,
    )
    db.add(new_course_build)
    db.commit()
    db.refresh(new_course_build)
    return new_course_build


def get_course_builds(db: Session, academic_year, instructor_email):
    course_builds = db.query(CourseBuild)

    if academic_year:
        course_builds = course_builds.filter(CourseBuild.academic_year == academic_year)

    if instructor_email:
        course_builds = course_builds.filter(
            func.lower(CourseBuild.instructor_email) == func.lower(instructor_email)
        )

    return course_builds.all()


def get_course_by_shortname(db: Session, course_shortname):
    course = (
        db.query(CourseBuild)
        .filter(CourseBuild.course_shortname == course_shortname)
        .first()
    )
    return course

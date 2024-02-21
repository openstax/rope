from sqlalchemy.orm import Session
from rope.db.schema import CourseBuild


def moodle_settings_key_check(moodle_setting_keys):
    moodle_setting_keys_to_check = [
        "academic_year",
        "academic_year_short",
        "course_category",
        "base_course_id",
    ]
    moodle_setting_keys_present = [
        key for key in moodle_setting_keys_to_check if key in moodle_setting_keys
    ]
    return moodle_setting_keys_present == moodle_setting_keys_to_check


def create_course_name(course_build_settings, moodle_settings):
    instructor_firstname = course_build_settings.instructor_firstname
    instructor_lastname = course_build_settings.instructor_lastname
    academic_year = moodle_settings["academic_year"]
    course_name = (
        f"Algebra 1 - {instructor_firstname} {instructor_lastname} {academic_year}"
    )
    return course_name


def create_course_shortname(course_build_settings, moodle_settings, update_shortname):
    instructor_firstname = course_build_settings.instructor_firstname
    instructor_lastname = course_build_settings.instructor_lastname
    academic_year_short = moodle_settings["academic_year_short"]
    course_shortname = (
        f"Alg1 {instructor_firstname[0]}{instructor_lastname[0]} {academic_year_short}"
    )
    nonce = 0
    if update_shortname:
        nonce += 1
        course_shortname = f"Alg1 {instructor_firstname[0]}{instructor_lastname[0]}{nonce} {academic_year_short}"
    return course_shortname


def update_course_shortname(
    db: Session,
    current_course_shortname,
    course_shortname_exists,
    course_build_settings,
    moodle_settings,
):
    # Need to also query moodle to confirm the shortname doesn't exist there as well.
    course_shortname = current_course_shortname
    while course_shortname_exists is not None:
        course_shortname = create_course_shortname(
            course_build_settings, moodle_settings, True
        )
        course_shortname_exists = (
            db.query(CourseBuild)
            .filter(CourseBuild.course_shortname == course_shortname)
            .first()
        )
    return course_shortname

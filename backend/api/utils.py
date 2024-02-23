from sqlalchemy.orm import Session
from rope.api import database


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
        course_shortname = f"Alg1 {instructor_firstname[0]}{instructor_lastname[0]}{nonce} {academic_year_short}"  # noqa: E501
    return course_shortname


def update_course_shortname(
    db: Session,
    current_course_shortname,
    course_shortname_exists,
    course_build_settings,
    moodle_settings,
    moodle_client=None,
):
    course_shortname = current_course_shortname
    if isinstance(course_shortname_exists, list):
        while len(course_shortname_exists) > 0:
            course_shortname = create_course_shortname(
                course_build_settings,
                moodle_settings,
                True,
            )
            get_moodle_course_by_shortname = moodle_client.get_course_by_shortname(
                course_shortname
            )
            course_shortname_exists = get_moodle_course_by_shortname["courses"]
    else:
        while course_shortname_exists is not None:
            course_shortname = create_course_shortname(
                course_build_settings, moodle_settings, True
            )
            course_shortname_exists = database.get_course_by_shortname(
                db,
                course_shortname,
            )
    return course_shortname

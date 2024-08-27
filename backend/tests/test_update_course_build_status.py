import pytest

from rope.db.schema import CourseBuild, SchoolDistrict, UserAccount
from rope.scripts import update_course_build_status


@pytest.fixture(autouse=True)
def clear_course_build_table(db):
    db.query(CourseBuild).delete()
    db.query(UserAccount).delete()
    db.query(SchoolDistrict).delete()
    db.commit()


@pytest.fixture
def setup_school_district(db):
    school_district = SchoolDistrict(name="westeros", active=True)
    db.add(school_district)
    db.commit()
    db.refresh(school_district)

    return school_district


@pytest.fixture
def setup_new_user_manager(db):
    user = UserAccount(email="vtargaryen@westeros.edu", is_manager=True, is_admin=False)
    db.add(user)
    db.commit()
    db.refresh(user)

    return user


def test_update_course_build_status(db, setup_school_district, setup_new_user_manager):
    school_district_id = setup_school_district.id
    user_id = setup_new_user_manager.id
    add_db_course_build = CourseBuild(
        instructor_firstname="Rhaenyra",
        instructor_lastname="Targaryen",
        instructor_email="rtargaryen@westeros.edu",
        course_name="Algebra 1 - Rhaenyra Targaryen (AY 2025)",
        course_shortname="Alg1 RT AY25",
        course_category_id="21",
        course_id=None,
        course_enrollment_url=None,
        course_enrollment_key=None,
        school_district_id=school_district_id,
        academic_year="AY 2025",
        academic_year_short="AY25",
        base_course_id="2121",
        status="failed",
        creator_id=user_id,
    )

    db.add(add_db_course_build)
    db.commit()
    course_builds = db.query(CourseBuild).all()

    course_build_id = course_builds[0].id
    update_course_build_status.update_course_build_status(course_build_id)
    db.refresh(course_builds[0])

    assert course_builds[0].status == "created"

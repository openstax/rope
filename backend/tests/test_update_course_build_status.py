import pytest

from rope.db.schema import CourseBuild, SchoolDistrict, UserAccount
from rope.scripts import update_course_build_status
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker


@pytest.fixture(autouse=True)
def clear_course_build_table(db):
    db.query(CourseBuild).delete()
    db.query(UserAccount).delete()
    db.query(SchoolDistrict).delete()
    db.execute(text("ALTER SEQUENCE course_build_id_seq RESTART WITH 1"))
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


def test_update_course_build_status(
    db, setup_school_district, setup_new_user_manager, mocker
):
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

    mocker.patch("sys.argv", ["", "1"])

    engine = create_engine("postgresql://pguser:pgpassword@localhost/ropedb")
    mock_factory = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    mocker.patch(
        "rope.scripts.update_course_build_status.get_db",
        lambda: mock_factory,
    )

    db.add(add_db_course_build)
    db.commit()

    update_course_build_status.main()
    course_builds = db.query(CourseBuild).all()
    updated_course_build = course_builds[0]

    assert updated_course_build.status == "created"

import argparse
from rope.db.schema import CourseBuild, CourseBuildStatus
from rope.api import database


session_factory = database.SessionLocal


# This function allows the code to be testable and
# talk to the mocked sessionmaker in test_update_course_build_status.py
def get_db():
    return session_factory  # pragma: no cover


def update_course_build_status(course_build_id):
    get_sessionmaker = get_db()
    with get_sessionmaker() as session:
        course_build = (
            session.query(CourseBuild).filter(CourseBuild.id == course_build_id).one()
        )
        course_build.status = CourseBuildStatus.CREATED.value
        session.commit()


def main():
    parser = argparse.ArgumentParser(description="")
    parser.add_argument(
        "course_build_id",
        type=int,
        help="Enter the course_build.id associated with the unsuccessful course build",
    )

    args = parser.parse_args()
    course_build_id = args.course_build_id

    update_course_build_status(course_build_id)


if __name__ == "__main__":
    main()  # pragma: no cover

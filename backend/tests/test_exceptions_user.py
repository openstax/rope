from sqlalchemy.exc import NoResultFound

import pytest

from rope.db.schema import UserAccount


@pytest.fixture(autouse=True)
def clear_database_table(db):
    db.query(UserAccount).delete()
    db.commit()


def test_non_admin_access_admin_endpoint(
    test_client,
    setup_override_get_request_session,
    mocker,
):
    user = {
        "12345": {
            "email": "test@rice.edu",
            "is_manager": False,
            "is_admin": False,
        }
    }
    mocker.patch(
        "rope.api.sessions.session_store",
        user,
    )
    non_admin_user = {
        "email": "createduser@rice.edu",
        "is_manager": False,
        "is_admin": False,
    }

    get_all_users_response = test_client.get("/user")
    create_user_response = test_client.post("/user", json=non_admin_user)
    update_user_response = test_client.put("/user/12", json=non_admin_user)
    delete_user_response = test_client.delete("/user/12")

    assert get_all_users_response.status_code == 403
    assert create_user_response.status_code == 403
    assert update_user_response.status_code == 403
    assert delete_user_response.status_code == 403


def test_missing_session_id(test_client, setup_override_empty_get_request_session):
    response = test_client.get("/user/current")

    assert response.status_code == 401


def test_update_db_user_no_results(test_client, db, setup_admin_session):
    with pytest.raises(NoResultFound) as exc_info:
        db_user = UserAccount(
            email="currentuser@rice.edu", is_manager=False, is_admin=False
        )
        db.add(db_user)
        db.commit()
        user = db.query(UserAccount).first()
        user_id = user.id
        updated_user_data = {
            "id": 1235235352,
            "email": "updateduser@rice.edu",
            "is_manager": False,
            "is_admin": False,
        }
        test_client.put(f"user/{user_id}", json=updated_user_data)

    assert exc_info.type is NoResultFound


def test_delete_db_user_no_results(test_client, setup_admin_session):
    response = test_client.delete(f"user/{12352353525324}")

    assert response.status_code == 404

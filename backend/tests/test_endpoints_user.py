import pytest

from rope.db.schema import UserAccount


@pytest.fixture(autouse=True)
def clear_database_table(db):
    db.query(UserAccount).delete()
    db.commit()


def test_get_current_user(test_client, setup_nonadmin_authenticated_user_session):
    response = test_client.get("/user/current")
    data = response.json()

    assert response.status_code == 200
    assert data["email"] == "test@rice.edu"
    assert data["is_manager"] is False
    assert data["is_admin"] is False


def test_unauthenticated_user(test_client, setup_override_get_request_session, mocker):
    user = {
        "ABCDEFG": {
            "email": "test@rice.edu",
            "is_manager": False,
            "is_admin": False,
        }
    }
    mocker.patch(
        "rope.api.sessions.session_store",
        user,
    )
    response = test_client.get("/user/current")

    assert response.status_code == 401


def test_get_all_users(test_client, db, setup_admin_session):
    db_user = UserAccount(email="test@rice.edu", is_manager=False, is_admin=False)
    db_user2 = UserAccount(email="admin@rice.edu", is_manager=False, is_admin=True)
    db.add(db_user)
    db.add(db_user2)
    db.commit()
    response = test_client.get("/user")
    data = response.json()

    assert response.status_code == 200
    assert len(data) == 2
    assert data[0].get("id") is not None
    assert data[1].get("id") is not None
    assert data[0].get("email") == "test@rice.edu"
    assert data[0].get("is_manager") is False
    assert data[0].get("is_admin") is False
    assert data[1].get("email") == "admin@rice.edu"
    assert data[1].get("is_manager") is False
    assert data[1].get("is_admin") is True


def test_create_user(test_client, db, setup_admin_session):
    new_user_data = {
        "email": "createduser@rice.edu",
        "is_manager": False,
        "is_admin": False,
    }
    response = test_client.post("/user", json=new_user_data)
    users = db.query(UserAccount).all()
    data = response.json()

    assert response.status_code == 200
    assert len(users) == 1
    assert data["email"] == "createduser@rice.edu"
    assert data["is_manager"] is False
    assert data["is_admin"] is False
    assert data.get("id") is not None


def test_update_user(test_client, db, setup_admin_session):
    db_user = UserAccount(
        email="currentuser@rice.edu", is_manager=False, is_admin=False
    )
    db.add(db_user)
    db.commit()
    user = db.query(UserAccount).first()
    user_id = user.id
    updated_user_data = {
        "id": user_id,
        "email": "updateduser@rice.edu",
        "is_manager": False,
        "is_admin": False,
    }
    response = test_client.put(f"user/{user_id}", json=updated_user_data)
    data = response.json()

    assert response.status_code == 200
    assert data["email"] == "updateduser@rice.edu"
    assert data["is_manager"] is False
    assert data["is_admin"] is False
    assert data.get("id") is not None


def test_delete_user(test_client, db, setup_admin_session):
    db_user = UserAccount(
        email="currentuser@rice.edu", is_manager=False, is_admin=False
    )
    db.add(db_user)
    db.commit()
    user = db.query(UserAccount).first()
    user_id = user.id
    response = test_client.delete(f"user/{user_id}")
    empty_db = db.query(UserAccount).all()

    assert response.status_code == 200
    assert len(empty_db) == 0

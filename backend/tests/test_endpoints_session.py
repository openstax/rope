import pytest

from rope.api.sessions import session_store
from rope.db.schema import UserAccount


@pytest.fixture(autouse=True)
def clear_database_table(db):
    db.query(UserAccount).delete()
    db.commit()


def test_delete_session(
    test_client,
    setup_override_get_request_session,
    mocker,
):
    session_store = {"12345": "ewfnweoif"}
    mocker.patch(
        "rope.api.sessions.session_store",
        session_store,
    )
    response = test_client.delete("/session")

    assert response.status_code == 200
    assert session_store.get("12345") is None


def test_google_login(test_client, db, mocker):
    google_oauth_mock = mocker.Mock()
    google_oauth_mock.verify_oauth2_token.return_value = {
        "hd": "rice.edu",
        "email": "test@rice.edu",
    }
    mocker.patch(
        "rope.api.auth.id_token.verify_oauth2_token",
        google_oauth_mock.verify_oauth2_token,
    )
    db_user = UserAccount(email="test@rice.edu", is_manager=False, is_admin=False)
    db.add(db_user)
    db.commit()
    response = test_client.post("/session", json={"token": "fp2m3fpwimef"})
    session_id = list(session_store.keys())[0]
    user_data = session_store[session_id]

    assert response.status_code == 200
    assert user_data["email"] == "test@rice.edu"
    assert user_data["is_manager"] is False
    assert user_data["is_admin"] is False

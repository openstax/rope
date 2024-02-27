import pytest

from rope.db.schema import UserAccount


@pytest.fixture(autouse=True)
def clear_database_table(db):
    db.query(UserAccount).delete()
    db.commit()


def test_missing_session_id(test_client, setup_override_empty_get_request_session):
    response = test_client.delete("/session")

    assert response.status_code == 401


def test_incorrect_user_domain(test_client, mocker):
    google_oauth_mock = mocker.Mock()
    google_oauth_mock.verify_oauth2_token.return_value = {
        "hd": "school.edu",
        "email": "test123@school.edu",
    }
    mocker.patch(
        "rope.api.auth.id_token.verify_oauth2_token",
        google_oauth_mock.verify_oauth2_token,
    )
    response = test_client.post("/session", json={"token": "fp2m3fpwim433tef"})

    assert response.status_code == 401


def test_verify_google_token_valueerror(test_client):
    response = test_client.post("/session", json={"token": "asd32fp2m3fpwim433tef"})

    assert response.status_code == 401


def test_get_user_by_email_no_results(test_client, db, mocker):
    google_oauth_mock = mocker.Mock()
    google_oauth_mock.verify_oauth2_token.return_value = {
        "hd": "rice.edu",
        "email": "test@rice.edu",
    }
    mocker.patch(
        "rope.api.auth.id_token.verify_oauth2_token",
        google_oauth_mock.verify_oauth2_token,
    )
    db_user = UserAccount(
        email="differentuser@rice.edu", is_manager=False, is_admin=False
    )
    db.add(db_user)
    db.commit()
    response = test_client.post("/session", json={"token": "12345fp2m3fpwimef"})

    assert response.status_code == 401

from fastapi import Request

session_store = {}


def get_request_session(request: Request):
    return request.session  # pragma: no cover


def create_session(session_id, user_data):
    session_store[session_id] = user_data


def get_session(session_id):
    return session_store.get(session_id)


def destroy_session(session_id):
    del session_store[session_id]

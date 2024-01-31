from fastapi import Request

sessions = {}


def get_request_session(request: Request):
    return request.session


def create_session(session_id, user_data):
    sessions[session_id] = user_data


def get_session(session_id):
    return sessions.get(session_id)


def destroy_session(session_id):
    del sessions[session_id]

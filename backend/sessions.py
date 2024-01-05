sessions = {}


def create_session(session_id, data):
    sessions[session_id] = data


def get_session(session_id):
    return sessions.get(session_id)


def destroy_session(session_id):
    del sessions[session_id]

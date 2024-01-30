sessions = {}


def create_session(session_id, user_data):
    sessions[session_id] = user_data


def get_session(session_id):
    return sessions.get(session_id)

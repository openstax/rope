import os

SESSION_SECRET_KEY = os.getenv("SESSION_SECRET_KEY")
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")

PG_SERVER = os.getenv("POSTGRES_SERVER", "")
PG_DB = os.getenv("POSTGRES_DB", "")
PG_USER = os.getenv("POSTGRES_USER", "")
PG_PASSWORD = os.getenv("POSTGRES_PASSWORD", "")
MOODLE_TOKEN = os.getenv("MOODLE_TOKEN", "")
MOODLE_URL = os.getenv("MOODLE_URL", "")

SQS_QUEUE = os.getenv("SQS_QUEUE", "")
SQS_POLL_INTERVAL_MINS = os.getenv("SQS_POLL_INTERVAL_MINS", "")

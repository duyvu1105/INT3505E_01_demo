from datetime import datetime

# Shared in-memory datastore and credentials for the demo
payments_db = {}
api_keys = {
    "test_key_v1": {"user_id": "user_001", "version": "v1"},
    "test_token_v2": {"user_id": "user_001", "version": "v2"}
}

def now_iso():
    return datetime.utcnow().isoformat()

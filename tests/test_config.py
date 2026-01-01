from app.core.config import DATABASE_URL, SECRET_KEY

def test_config_loaded():
    assert DATABASE_URL is not None
    assert SECRET_KEY == "changeme"

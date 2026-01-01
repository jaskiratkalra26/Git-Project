from app.db.database import get_db, engine
from sqlalchemy import text

def test_database_connection():
    # Test that we can connect to the DB
    with engine.connect() as connection:
        result = connection.execute(text("SELECT 1"))
        assert result.scalar() == 1

def test_get_db():
    # Test the dependency
    gen = get_db()
    db = next(gen)
    assert db is not None
    # clean up
    try:
        next(gen)
    except StopIteration:
        pass

from src.config import settings
from src.database.sqlite import get_db as get_sqlite_db
from src.database.postgres import get_postgres_db

def get_db():
    """
    Factory function to get the appropriate database connection 
    based on the configured DATABASE_URL.
    """
    if "sqlite" in settings.DATABASE_URL:
        return get_sqlite_db()
    else:
        return get_postgres_db()

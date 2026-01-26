from langchain_community.utilities import SQLDatabase
from src.config import settings
import logging

logger = logging.getLogger(__name__)

def get_postgres_db() -> SQLDatabase:
    """
    Returns a LangChain SQLDatabase instance connected to PostgreSQL.
    """
    try:
        # include_tables=['sales_data'] ensures we only expose the sales table
        db = SQLDatabase.from_uri(
            settings.DATABASE_URL,
            include_tables=['sales_data'], 
            sample_rows_in_table_info=3
        )
        logger.info(f"Connected to PostgreSQL database at {settings.DATABASE_URL}")
        return db
    except Exception as e:
        logger.error(f"Failed to connect to PostgreSQL: {e}")
        raise e

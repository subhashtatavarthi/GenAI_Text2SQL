from fastapi import APIRouter, HTTPException
from src.models.schema_models import SchemaRequest, SchemaResponse, TableSchema, ColumnInfo
from sqlalchemy import create_engine, inspect, text
from urllib.parse import quote_plus
import logging

router = APIRouter(prefix="/api/v1", tags=["schema"])
logger = logging.getLogger(__name__)

@router.post("/get-schema", response_model=SchemaResponse)
async def get_schema(payload: SchemaRequest):
    """
    Connects to the specified database (SQLite/Postgres) and retrieves table schema information.
    """
    logger.info(f"Received schema request for type: {payload.type}")
    
    connection_url = ""
    
    # 1. Build Connection String
    try:
        if payload.type == "sqlite":
            path = payload.details.file_path or "sales.db"
            # Ensure it starts with proper prefix
            if "sqlite:///" not in path:
                # Handle relative paths for local dev ease
                if path.startswith("./") or path.startswith("/"):
                     connection_url = f"sqlite:///{path}"
                else:
                     connection_url = f"sqlite:///./{path}"
            else:
                connection_url = path
                
        elif payload.type == "postgres":
            d = payload.details
            if not all([d.host, d.username, d.password, d.database]):
                raise HTTPException(status_code=400, detail="Missing required Postgres details (host, user, pass, db)")
            
            # Safe URL construction
            # postgresql+psycopg2://user:pass@host:port/dbname
            user = quote_plus(d.username)
            password = quote_plus(d.password)
            host = d.host
            port = d.port
            dbname = d.database
            connection_url = f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{dbname}"
            
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported DB type: {payload.type}")

        logger.info(f"Connecting to {payload.type} at {connection_url.split('@')[-1]}") # Log safe part only

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error constructing connection string: {str(e)}")

    # 2. Connect and Reflect
    try:
        engine = create_engine(connection_url)
        inspector = inspect(engine)
        
        target_tables = []
        
        # Filter by table_name if provided
        all_tables = inspector.get_table_names()
        if payload.details.table_name:
            if payload.details.table_name in all_tables:
                target_tables = [payload.details.table_name]
            else:
                raise HTTPException(status_code=404, detail=f"Table '{payload.details.table_name}' not found")
        else:
            target_tables = all_tables
            
        table_schemas = []
        
        for table in target_tables:
            # Get Columns
            columns_data = inspector.get_columns(table)
            columns_info = []
            for col in columns_data:
                columns_info.append(ColumnInfo(
                    name=col['name'],
                    type=str(col['type']),
                    description="" # Empty for frontend/backend to fill
                ))
            
            table_schemas.append(TableSchema(
                table_name=table,
                columns=columns_info
            ))
            
        return SchemaResponse(
            dataset_id=payload.dataset_id,
            database_type=payload.type,
            database_name=payload.details.database or "sqlite_file",
            tables=table_schemas
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to fetch schema: {e}")
        raise HTTPException(status_code=500, detail=f"Database connection or reflection failed: {str(e)}")

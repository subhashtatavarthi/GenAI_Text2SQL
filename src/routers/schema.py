from fastapi import APIRouter, HTTPException
from src.models.schema_models import SchemaRequest, SchemaResponse, TableSchema, ColumnInfo
from sqlalchemy import create_engine, inspect, text
from urllib.parse import quote_plus
import os
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
            # Load Centralized Config (Text File)
            import configparser
            
            config = configparser.ConfigParser()
            # Path: project_root/config/postgres.config
            # __file__ is src/routers/schema.py
            # dirname(__file__) is src/routers
            # dirname(dirname(__file__)) is src
            # dirname(dirname(dirname(__file__))) is project_root
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            config_path = os.path.join(project_root, "config", "postgres.config")
            
            # Default values
            conf_host = "localhost"
            conf_port = "5432"
            conf_user = "postgres"
            conf_pass = os.getenv("POSTGRES_PASSWORD")
            
            # Optional: Legacy Config Overrides
            if os.path.exists(config_path):
                try:
                    config.read(config_path)
                    logger.info(f"Loaded config from {config_path}")
                    if "postgres" in config:
                        pg_conf = config["postgres"]
                        conf_host = pg_conf.get("host", conf_host)
                        conf_port = pg_conf.get("port", conf_port)
                        conf_user = pg_conf.get("user", conf_user)
                        raw_pass = pg_conf.get("password")
                        
                        if raw_pass:
                            if raw_pass.startswith("ENV:"):
                                env_var = raw_pass.split("ENV:")[1]
                                conf_pass = os.getenv(env_var)
                                logger.info(f"Resolved password from ENV:{env_var}: {'FOUND' if conf_pass else 'MISSING'}")
                            else:
                                conf_pass = raw_pass
                except Exception as e:
                    logger.warning(f"Error reading config file: {e}")
            else:
                 logger.info("No postgres.config found, using defaults and environment variables.")
            
            # Use Config values if payload values are missing/empty
            host = d.host or conf_host
            port = d.port or int(conf_port)
            user_name = d.username or conf_user
            password_val = d.password or conf_pass
            dbname = d.database
            
            if not all([host, user_name, password_val, dbname]):
                raise HTTPException(status_code=400, detail=f"Missing required Postgres details (User: {user_name}, Host: {host}). Ensure 'postgres.config' is set correctly.")

            # Safe URL construction
            # postgresql+psycopg2://user:pass@host:port/dbname
            if password_val is None:
                raise HTTPException(status_code=400, detail="Postgres password not found. Ensure POSTGRES_PASSWORD is set in .env or config.")
                
            user = quote_plus(user_name)
            password = quote_plus(password_val)
            
            connection_url = f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{dbname}"
            
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported DB type: {payload.type}")

        logger.info(f"Connecting to {payload.type} at {connection_url.split('@')[-1]}") # Log safe part only

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error constructing connection string: {str(e)}")

    # 2. Connect and Reflect
    try:
        connect_args = {}
        if payload.type == "postgres":
             connect_args = {"connect_timeout": 5}
             
        engine = create_engine(connection_url, connect_args=connect_args)
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

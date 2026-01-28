from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import uuid
import hashlib
import json
import os
import logging
from typing import List, Optional, Dict, Any
from sqlalchemy import create_engine, inspect
from urllib.parse import quote_plus
from datetime import datetime
from dotenv import load_dotenv

# Ensure env vars are loaded for password resolution
load_dotenv()

router = APIRouter(prefix="/api/v1", tags=["onboarding"])
logger = logging.getLogger(__name__)

# Config Path for Table Registry
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
REGISTRY_PATH = os.path.join(PROJECT_ROOT, "config", "postgres_tables.json")
SQLITE_REGISTRY_PATH = os.path.join(PROJECT_ROOT, "config", "sqlite_tables.json")
POSTGRES_META_PATH = os.path.join(PROJECT_ROOT, "config", "postgres_metadata.json")
SQLITE_META_PATH = os.path.join(PROJECT_ROOT, "config", "sqlite_metadata.json")

# Ensure config dir exists
os.makedirs(os.path.join(PROJECT_ROOT, "config"), exist_ok=True)

class OnboardTableRequest(BaseModel):
    type: str = "postgres" # 'postgres' or 'sqlite'
    # Postgres fields
    host: Optional[str] = "localhost"
    port: Optional[int] = 5432
    database: Optional[str] = None
    table_name: str
    username: Optional[str] = None
    password: Optional[str] = None
    # SQLite Fields
    file_path: Optional[str] = None

class OnboardTableResponse(BaseModel):
    message: str
    table_id: str
    hash_key: str

def load_registry(path):
    if not os.path.exists(path):
        return {"instances": []} # Generic structure
    try:
        with open(path, 'r') as f:
            return json.load(f)
    except:
        return {"instances": []}

def save_registry(path, data):
    with open(path, 'w') as f:
        json.dump(data, f, indent=4)

# Helpers for Postgres specific structure 
def load_postgres_registry():
    if not os.path.exists(REGISTRY_PATH):
        return {"postgres_instances": [], "postgres_passwords": []}
    try:
        with open(REGISTRY_PATH, 'r') as f:
            return json.load(f)
    except:
         return {"postgres_instances": [], "postgres_passwords": []}

def save_postgres_registry(data):
    with open(REGISTRY_PATH, 'w') as f:
        json.dump(data, f, indent=4)

def generate_hash_key(host, db, table):
    raw = f"{host}:{db}:{table}"
    return hashlib.sha256(raw.encode()).hexdigest()

def generate_sqlite_hash(file_path):
    return hashlib.sha256(file_path.encode()).hexdigest()

def extract_and_save_schema(table_id, payload):
    """
    Connects to the DB, fetches columns, and updates appropriate metadata file
    """
    try:
        connection_url = ""
        target_tables = []
        metadata_path = ""
        
        if payload.type == "sqlite":
             metadata_path = SQLITE_META_PATH
             if "sqlite:///" not in payload.file_path:
                 # Handle relative paths 
                 if payload.file_path.startswith("./") or payload.file_path.startswith("/"):
                     connection_url = f"sqlite:///{payload.file_path}"
                 else:
                     connection_url = f"sqlite:///./{payload.file_path}"
             else:
                 connection_url = payload.file_path
             
        elif payload.type == "postgres":
             metadata_path = POSTGRES_META_PATH
             user = payload.username or "postgres"
             pwd = payload.password
             
             if not pwd or pwd.startswith("ENV:"):
                 env_var = "POSTGRES_PASSWORD"
                 if pwd and pwd.startswith("ENV:"):
                     env_var = pwd.split("ENV:")[1]
                 pwd = os.getenv(env_var)
             
             if not pwd:
                 logger.warning("No password found for schema extraction")
                 return
                 
             user = quote_plus(user)
             password = quote_plus(pwd)
             host = payload.host
             port = payload.port
             db = payload.database
             connection_url = f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{db}"
             target_tables = [payload.table_name]
             
        # Connect
        logger.info(f"Extracting schema from {connection_url.split('@')[-1]}")
        engine = create_engine(connection_url)
        inspector = inspect(engine)
        
        if not target_tables:
            target_tables = inspector.get_table_names()
            
        columns_list = []
        
        for t_name in target_tables:
            cols = inspector.get_columns(t_name)
            for c in cols:
                col_name = c['name']
                if len(target_tables) > 1:
                    col_name = f"{t_name}.{c['name']}"
                
                columns_list.append({
                    "name": col_name,
                    "type": str(c['type']),
                    "description": ""
                })
                
        # Load Metadata
        meta = {}
        if os.path.exists(metadata_path):
            with open(metadata_path, 'r') as f:
                try:
                    meta = json.load(f)
                except:
                    meta = {}
                    
        meta[table_id] = {
            "description": f"Imported from {payload.type}",
            "columns": columns_list
        }
        
        with open(metadata_path, 'w') as f:
            json.dump(meta, f, indent=4)
            
        logger.info(f"Schema extracted and saved for {table_id} to {os.path.basename(metadata_path)}")
        
    except Exception as e:
        logger.error(f"Failed to extract schema for {table_id}: {e}")

@router.post("/onboard-table", response_model=OnboardTableResponse)
async def onboard_table(payload: OnboardTableRequest):
    if payload.type == 'sqlite':
        return await onboard_sqlite(payload)
    else:
        return await onboard_postgres(payload)

async def onboard_sqlite(payload: OnboardTableRequest):
    registry = load_registry(SQLITE_REGISTRY_PATH)
    hash_key = generate_sqlite_hash(payload.file_path)
    
    # Check uniqueness
    for inst in registry.get("instances", []):
         if inst.get("hash_key") == hash_key:
             raise HTTPException(status_code=409, detail="Database file already onboarded.")
             
    table_id = str(uuid.uuid4())
    new_instance = {
        "table_id": table_id,
        "type": "sqlite",
        "file_path": payload.file_path,
        "table_name": payload.table_name,
        "hash_key": hash_key,
        "onboarded_by": "Admin",
        "onboarded_at": datetime.now().isoformat()
    }
    
    if "instances" not in registry:
        registry["instances"] = []
    registry["instances"].append(new_instance)
    
    save_registry(SQLITE_REGISTRY_PATH, registry)
    
    # Extract Schema
    extract_and_save_schema(table_id, payload)
    
    return OnboardTableResponse(
        message="SQLite Database onboarded",
        table_id=table_id,
        hash_key=hash_key
    )

async def onboard_postgres(payload: OnboardTableRequest):
    logger.info(f"Onboarding table: {payload.table_name} in {payload.database}@{payload.host}")
    registry = load_postgres_registry()
    table_id = str(uuid.uuid4())
    hash_key = generate_hash_key(payload.host, payload.database, payload.table_name)
    
    for inst in registry.get("postgres_instances", []):
        if inst.get("postgress_hash_key") == hash_key:
             raise HTTPException(status_code=409, detail="Table already exists.")
    
    passwords_list = registry.get("postgres_passwords", [])
    host_entry = next((item for item in passwords_list if item["postgress_hostname"] == payload.host), None)
    
    if not host_entry:
         pwd_val = payload.password or "ENV:POSTGRES_PASSWORD"
         passwords_list.append({
             "postgress_hostname": payload.host,
             "postgress_password": pwd_val
         })
         registry["postgres_passwords"] = passwords_list

    new_instance = {
        "table_id": table_id,
        "postgress_user": payload.username or "postgres",
        "postgress_password": "ENV:POSTGRES_PASSWORD",
        "postgress_hostname": payload.host,
        "postgress_port": str(payload.port),
        "postgress_database": payload.database,
        "postgress_table": payload.table_name,
        "postgress_hash_key": hash_key,
        "onboarded_by": "Admin",
        "onboarded_at": datetime.now().isoformat()
    }
    
    if "postgres_instances" not in registry:
        registry["postgres_instances"] = []
    registry["postgres_instances"].append(new_instance)
    
    save_postgres_registry(registry)
    
    # Extract Schema
    extract_and_save_schema(table_id, payload)
    
    return OnboardTableResponse(
        message="Table successfully onboarded",
        table_id=table_id,
        hash_key=hash_key
    )

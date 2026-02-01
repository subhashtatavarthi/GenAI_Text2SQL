from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import json
import os
import logging
from typing import List, Optional, Dict, Any

router = APIRouter(prefix="/api/v1", tags=["tables"])
logger = logging.getLogger(__name__)

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
POSTGRES_REGISTRY = os.path.join(PROJECT_ROOT, "config", "postgres_tables.json")
SQLITE_REGISTRY = os.path.join(PROJECT_ROOT, "config", "sqlite_tables.json")
POSTGRES_META = os.path.join(PROJECT_ROOT, "config", "postgres_metadata.json")
SQLITE_META = os.path.join(PROJECT_ROOT, "config", "sqlite_metadata.json")
PROMPT_CONFIG = os.path.join(PROJECT_ROOT, "config", "prompt.config")

class PromptConfigRequest(BaseModel):
    table_id: str
    table_name: str
    database_type: str
    Prompt: str

@router.get("/tables/{table_id}/prompt")
async def get_table_prompt(table_id: str):
    data = load_json(PROMPT_CONFIG)
    if table_id in data:
        return data[table_id]
    return {"table_id": table_id, "Prompt": ""}

@router.post("/tables/{table_id}/prompt")
async def save_table_prompt(table_id: str, payload: PromptConfigRequest):
    data = load_json(PROMPT_CONFIG)
    data[table_id] = payload.dict()
    save_json(PROMPT_CONFIG, data)
    return {"status": "success", "message": "Prompt configuration saved"}

class TableSummary(BaseModel):
    table_id: str
    name: str # table_name or file_path
    type: str # 'postgres' or 'sqlite'
    db_name: Optional[str] = None
    description: Optional[str] = ""
    onboarded_by: Optional[str] = "Admin"
    onboarded_at: Optional[str] = ""

class ColumnMetadata(BaseModel):
    name: str
    type: str
    description: str

class TableMetadataRequest(BaseModel):
    description: str
    columns: List[ColumnMetadata]

def load_json(path):
    if not os.path.exists(path):
        return {}
    try:
        with open(path, 'r') as f:
            return json.load(f)
    except:
        return {}

def save_json(path, data):
    with open(path, 'w') as f:
        json.dump(data, f, indent=4)

@router.get("/tables", response_model=List[TableSummary])
async def list_tables():
    tables = []
    
    # Load Metadata
    pg_meta = load_json(POSTGRES_META)
    sl_meta = load_json(SQLITE_META)
    
    # Load Postgres
    pg_data = load_json(POSTGRES_REGISTRY)
    for inst in pg_data.get("postgres_instances", []):
         tid = inst.get("table_id")
         desc = ""
         if tid in pg_meta:
             desc = pg_meta[tid].get("description", "")
             
         tables.append(TableSummary(
             table_id=tid,
             name=inst.get("postgress_table"),
             type="postgres",
             db_name=inst.get("postgress_database"),
             description=desc,
             onboarded_by=inst.get("onboarded_by", "Admin"),
             onboarded_at=inst.get("onboarded_at", "")
         ))

    # Load SQLite
    sl_data = load_json(SQLITE_REGISTRY)
    for inst in sl_data.get("instances", []):
         tid = inst.get("table_id")
         desc = ""
         if tid in sl_meta:
             desc = sl_meta[tid].get("description", "")
             
         tables.append(TableSummary(
             table_id=tid,
             name=inst.get("table_name", inst.get("file_path")), 
             type="sqlite",
             db_name="SQLite",
             description=desc,
             onboarded_by=inst.get("onboarded_by", "Admin"),
             onboarded_at=inst.get("onboarded_at", "")
         ))
            
    return tables

@router.get("/tables/{table_id}/metadata")
async def get_table_metadata(table_id: str):
    # Check Postgres
    pg_meta = load_json(POSTGRES_META)
    if table_id in pg_meta:
        return pg_meta[table_id]
        
    # Check SQLite
    sl_meta = load_json(SQLITE_META)
    if table_id in sl_meta:
        return sl_meta[table_id]
        
    return {"description": "", "columns": []}

@router.post("/tables/{table_id}/metadata")
async def update_table_metadata(table_id: str, payload: TableMetadataRequest):
    # Check Postgres
    pg_meta = load_json(POSTGRES_META)
    if table_id in pg_meta:
        pg_meta[table_id] = payload.dict()
        save_json(POSTGRES_META, pg_meta)
        return {"status": "success", "message": "Metadata saved to Postgres registry"}
        
    # Check SQLite
    sl_meta = load_json(SQLITE_META)
    if table_id in sl_meta:
        sl_meta[table_id] = payload.dict()
        save_json(SQLITE_META, sl_meta)
        return {"status": "success", "message": "Metadata saved to SQLite registry"}
        
    # If not found, default to one based on... IDK?
    # Probably an error, but let's assume it's a new entry that got desynced?
    # Or just raise 404
    raise HTTPException(status_code=404, detail="Table metadata not found")

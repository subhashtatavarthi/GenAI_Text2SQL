from pydantic import BaseModel, Field
from typing import Literal, Optional, List, Dict, Any

class DBConnectionDetails(BaseModel):
    # Common
    host: Optional[str] = "localhost"
    port: Optional[int] = 5432
    database: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None
    
    # Specific to SQLite
    file_path: Optional[str] = None
    
    # Filtering
    table_name: Optional[str] = None

class SchemaRequest(BaseModel):
    type: Literal["sqlite", "postgres"] = Field(..., description="Database type: 'sqlite' or 'postgres'")
    dataset_id: Optional[str] = Field(None, description="Optional ID for tracking this dataset")
    details: DBConnectionDetails

class ColumnInfo(BaseModel):
    name: str
    type: str
    description: str = ""

class TableSchema(BaseModel):
    table_name: str
    columns: List[ColumnInfo]

class SchemaResponse(BaseModel):
    dataset_id: Optional[str]
    database_type: str
    database_name: Optional[str]
    tables: List[TableSchema]

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.config import settings
from src.routers import schema, query # We restore query router too if user wants to use agent later
from contextlib import asynccontextmanager
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up GenAI Text-to-SQL API...")
    yield
    logger.info("Shutting down...")

app = FastAPI(
    title=settings.APP_TITLE,
    version=settings.APP_VERSION,
    lifespan=lifespan
)

# CORS Configuration
origins = [
    "http://localhost:5173", # Vite
    "http://127.0.0.1:5173",
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(schema.router)
app.include_router(query.router)

@app.get("/health")
def health_check():
    return {"status": "ok", "version": settings.APP_VERSION}

@app.get("/")
def read_root():
    return {"message": f"Welcome to {settings.APP_TITLE} v{settings.APP_VERSION}"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.main:app", host="0.0.0.0", port=8000, reload=True)

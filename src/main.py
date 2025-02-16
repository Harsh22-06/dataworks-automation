from fastapi import FastAPI, HTTPException, Response, Query
from fastapi.responses import StreamingResponse
from pathlib import Path
from typing import Optional
from llm.parser import parse_task
from utils.security import secure_operation, validate_path
from tasks.operations.core_tasks import handle_phase_a
from tasks.business.business_tasks import handle_phase_b, router as business_router
from models import TaskRequest, TaskResponse
import mimetypes
from tasks.exceptions import TaskExecutionError, TaskParsingError
import logging
import sys
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

app = FastAPI()
DATA_DIR = Path("/data")
app.include_router(business_router, prefix="/api/v1")

@app.on_event("startup")
async def startup_event():
    """Log startup information"""
    logger.info("Starting FastAPI application...")
    logger.info(f"Data directory: {DATA_DIR}")
    logger.info("Python path: %s", sys.path)
    logger.info("Current working directory: %s", os.getcwd())
    logger.info("API endpoints initialized")
Write-Host "🔍 Debugging server connection..."

# Stop any existing containers
Write-Host "1. Cleaning up existing containers..."
podman stop dataworks-agent 2>$null
podman rm dataworks-agent 2>$null

# Start container in interactive mode
Write-Host "2. Starting container with verbose logging..."
podman run `
    --name dataworks-agent `
    -p 8000:8000 `
    -e AIPROXY_TOKEN="$env:AIPROXY_TOKEN" `
    -e PYTHONUNBUFFERED=1 `
    -e LOG_LEVEL=DEBUG `
    -v "${PWD}/test-data:/data" `
    localhost/dataworks-agent
@app.post("/run", response_model=TaskResponse)  # Add response model
@secure_operation
async def run_task(task: str = Query(..., description="Task description to execute")):
    try:
        # Parse natural language task
        task_details = parse_task(task)
        
        # Execute task
        if task_details['phase'] == 'A':
            result = handle_phase_a(task_details)
        elif task_details['phase'] == 'B':
            result = handle_phase_b(task_details)
        else:
            raise ValueError(f"Unknown phase: {task_details['phase']}")
            
        return result
    except TaskParsingError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except TaskExecutionError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

@app.get("/read")
async def read_file(path: str = Query(..., description="Path to file")):
    file_path = DATA_DIR / path.lstrip('/')
    if not validate_path(file_path):
        raise HTTPException(403, "Access denied")
    if not file_path.exists():
        raise HTTPException(404, detail="File not found")
    return file_path.read_text()

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

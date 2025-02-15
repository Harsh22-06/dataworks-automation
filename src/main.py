from fastapi import FastAPI, HTTPException
from pathlib import Path
import subprocess
from llm.parser import parse_task
from utils.security import secure_operation, validate_path

app = FastAPI()
DATA_DIR = Path("/data")

@app.post("/run")
@secure_operation
async def run_task(task: str):
    try:
        task_details = parse_task(task)
        
        # Validate input/output paths
        for path in [task_details.get('input_path'), task_details.get('output_path')]:
            if path and not validate_path(Path(path)):
                raise HTTPException(403, "Invalid file path")
        
        # Execute task
        if task_details['phase'] == 'A':
            from tasks.operations.core_tasks import handle_phase_a
            handle_phase_a(task_details)
        else:
            from tasks.business.business_tasks import handle_phase_b
            handle_phase_b(task_details)
            
        return {"status": "success"}
    
    except ValueError as e:
        raise HTTPException(400, str(e))
    except Exception as e:
        raise HTTPException(500, str(e))

@app.get("/read")
async def read_file(path: str):
    file_path = DATA_DIR / path.lstrip('/')
    if not validate_path(file_path):
        raise HTTPException(403, "Access denied")
    if not file_path.exists():
        raise HTTPException(404)
    return file_path.read_text()

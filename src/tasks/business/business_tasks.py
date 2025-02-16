from fastapi import APIRouter, HTTPException
from pathlib import Path
import requests
import git
from PIL import Image
import markdown
import pandas as pd
import duckdb
import whisper
import subprocess
from typing import Dict, Any
from config import settings
from utils.security import validate_path
import sqlite3  # Add this import

router = APIRouter()

def handle_phase_b(task_details: Dict[str, Any]) -> Dict[str, Any]:
    """Handle business automation tasks with security constraints"""
    try:
        operation = task_details['operation']
        
        if operation == 'B3':
            # Fetch API data
            response = requests.get(
                task_details['parameters']['api_url'],
                timeout=30,
                verify=True  # Ensure SSL verification
            )
            response.raise_for_status()
            
            output_path = Path(settings.data_dir) / task_details['output_path']
            if not validate_path(output_path):
                raise ValueError("Invalid output path")
                
            output_path.write_text(response.text)
            return {"status": "success", "message": "API data saved successfully"}

        elif operation == 'B4':
            # Git operations (restricted to /data)
            repo_path = Path(settings.data_dir) / 'repo'
            if task_details['parameters'].get('repo_url'):
                # Clone only if repo doesn't exist
                if not repo_path.exists():
                    git.Repo.clone_from(
                        task_details['parameters']['repo_url'],
                        repo_path
                    )
                repo = git.Repo(repo_path)
                # Make changes and commit
                file_path = repo_path / task_details['parameters']['file_path']
                if not validate_path(file_path):
                    raise ValueError("Invalid file path for git operations")
                    
                file_path.write_text(task_details['parameters']['content'])
                repo.index.add([str(file_path)])
                repo.index.commit(task_details['parameters']['commit_message'])
                
            return {"status": "success", "message": "Git operations completed"}

        elif operation == 'B5':
            # Database operations
            db_path = Path(settings.data_dir) / task_details['parameters']['db_path']
            if not validate_path(db_path):
                raise ValueError("Invalid database path")
                
            query = task_details['parameters']['query']
            if any(op.lower() in query.lower() 
                  for op in settings.security.restricted_operations):
                raise ValueError("Query contains restricted operations")
                
            if db_path.suffix == '.db':
                # SQLite
                conn = sqlite3.connect(db_path)
                result = pd.read_sql_query(query, conn)
                conn.close()
            else:
                # DuckDB
                conn = duckdb.connect(str(db_path))
                result = conn.execute(query).fetchdf()
                conn.close()
                
            output_path = Path(settings.data_dir) / task_details['output_path']
            if not validate_path(output_path):
                raise ValueError("Invalid output path")
                
            result.to_csv(output_path, index=False)
            return {"status": "success", "message": "Query executed successfully"}

        elif operation == 'B6':
            # Web scraping with security constraints
            response = requests.get(
                task_details['parameters']['url'],
                timeout=30,
                verify=True
            )
            response.raise_for_status()
            
            output_path = Path(settings.data_dir) / task_details['output_path']
            if not validate_path(output_path):
                raise ValueError("Invalid output path")
                
            output_path.write_text(response.text)
            return {"status": "success", "message": "Website data scraped successfully"}

        elif operation == 'B7':
            # Image processing
            input_path = Path(settings.data_dir) / task_details['input_path']
            output_path = Path(settings.data_dir) / task_details['output_path']
            
            if not validate_path(input_path) or not validate_path(output_path):
                raise ValueError("Invalid input or output path")
                
            with Image.open(input_path) as img:
                # Process image based on parameters
                if task_details['parameters'].get('resize'):
                    width, height = task_details['parameters']['resize']
                    img = img.resize((width, height), Image.Resampling.LANCZOS)
                elif task_details['parameters'].get('compress'):
                    quality = task_details['parameters']['compress']
                    img.save(output_path, quality=quality, optimize=True)
                else:
                    img.save(output_path)
                    
            return {"status": "success", "message": "Image processed successfully"}

        elif operation == 'B8':
            # Audio transcription
            input_path = Path(settings.data_dir) / task_details['input_path']
            output_path = Path(settings.data_dir) / task_details['output_path']
            
            if not validate_path(input_path) or not validate_path(output_path):
                raise ValueError("Invalid input or output path")
                
            model = whisper.load_model("base")
            result = model.transcribe(str(input_path))
            
            output_path.write_text(result["text"])
            return {"status": "success", "message": "Audio transcribed successfully"}

        elif operation == 'B9':
            # Markdown to HTML conversion
            input_path = Path(settings.data_dir) / task_details['input_path']
            output_path = Path(settings.data_dir) / task_details['output_path']
            
            if not validate_path(input_path) or not validate_path(output_path):
                raise ValueError("Invalid input or output path")
                
            md_content = input_path.read_text()
            html_content = markdown.markdown(md_content)
            output_path.write_text(html_content)
            
            return {"status": "success", "message": "Markdown converted successfully"}

        elif operation == 'B10':
            # CSV filtering API endpoint
            return {"status": "success", "message": "Use /api/v1/filter-csv endpoint"}

        else:
            raise ValueError(f"Unknown operation: {operation}")

    except Exception as e:
        raise TaskExecutionError(f"Task execution failed: {str(e)}")

@router.get("/filter-csv")
async def filter_csv(file_path: str, column: str, value: str):
    """B10: Filter CSV and return JSON data"""
    try:
        path = Path(settings.data_dir) / file_path
        if not validate_path(path):
            raise HTTPException(status_code=403, detail="Access denied")
            
        df = pd.read_csv(path)
        filtered = df[df[column] == value]
        return filtered.to_dict(orient='records')
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

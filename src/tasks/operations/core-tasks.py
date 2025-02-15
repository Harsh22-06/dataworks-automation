from pathlib import Path
import subprocess
import json
import sqlite3
from datetime import datetime
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from openai import OpenAI

client = OpenAI(api_key=os.environ["AIPROXY_TOKEN"])
DATA_DIR = Path("/data")

def handle_phase_a(task_details):
    operation = task_details['operation']
    
    if operation == 'A1':
        subprocess.run(["uv", "pip", "install", "-r", "requirements.txt"])
        subprocess.run([
            "python", 
            "https://raw.githubusercontent.com/sanand0/tools-in-data-science-public/tds-2025-01/project-1/datagen.py",
            task_details['parameters']['user_email']
        ])
    
    elif operation == 'A2':
        subprocess.run([
            "npx", "prettier@3.4.2",
            "--write", str(DATA_DIR / "format.md"),
            "--parser", "markdown"
        ])
    
    # Add similar handlers for A3-A10
    # Example for A3:
    elif operation == 'A3':
        input_path = DATA_DIR / "dates.txt"
        output_path = DATA_DIR / "dates-wednesdays.txt"
        count = 0
        with open(input_path) as f:
            for line in f:
                date = datetime.strptime(line.strip(), "%Y-%m-%d")
                if date.weekday() == 2:  # Wednesday
                    count += 1
        output_path.write_text(str(count))

from pathlib import Path
import subprocess
import json
import sqlite3
from datetime import datetime
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from openai import OpenAI
import os
from config import settings
import glob
from typing import Dict, Any
import base64
import numpy as np
from .exceptions import TaskExecutionError

DATA_DIR = Path(settings.data_dir)
client = OpenAI(api_key=settings.aiproxy_token)

def handle_phase_a(task_details: Dict[str, Any]) -> Dict[str, Any]:
    """Execute Phase A tasks with proper error handling"""
    try:
        operation = task_details['operation']
        input_path = task_details.get('input_path')
        output_path = task_details.get('output_path')
        
        # Validate paths
        if input_path:
            input_path = DATA_DIR / input_path.lstrip('/')
            if not input_path.exists():
                raise FileNotFoundError(f"Input file not found: {input_path}")
                
        if output_path:
            output_path = DATA_DIR / output_path.lstrip('/')
            output_path.parent.mkdir(parents=True, exist_ok=True)

        # Execute task based on operation
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
        
        elif operation == 'A3':  # Example for date counting
            if not input_path or not output_path:
                raise ValueError("Missing input or output path")
                
            count = count_weekday_occurrences(
                input_path,
                weekday=task_details.get('parameters', {}).get('weekday', 2)  # Default to Wednesday
            )
            output_path.write_text(str(count))
        
        elif operation == 'A4':
            with open(DATA_DIR / "contacts.json") as f:
                data = json.load(f)
            
            sorted_contacts = sorted(
                data['contacts'],
                key=lambda x: (x['last_name'], x['first_name'])
            )
            
            with open(DATA_DIR / "contacts-sorted.json", 'w') as f:
                json.dump({'contacts': sorted_contacts}, f, indent=2)
        
        elif operation == 'A5':
            log_files = list(DATA_DIR.glob('logs/*.log'))
            log_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
            
            with open(DATA_DIR / "logs-recent.txt", 'w') as out:
                for log_file in log_files[:10]:
                    with open(log_file) as f:
                        first_line = f.readline().strip()
                        out.write(f"{first_line}\n")
        
        elif operation == 'A6':
            index = {}
            docs_dir = DATA_DIR / "docs"
            
            for md_file in docs_dir.glob('**/*.md'):
                relative_path = str(md_file.relative_to(docs_dir))
                with open(md_file) as f:
                    for line in f:
                        if line.startswith('# '):
                            index[relative_path] = line[2:].strip()
                            break
            
            with open(docs_dir / "index.json", 'w') as f:
                json.dump(index, f, indent=2)
        
        elif operation == 'A7':
            with open(DATA_DIR / "email.txt") as f:
                email_content = f.read()
            
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Extract the sender's email address from the email content."},
                    {"role": "user", "content": email_content}
                ]
            )
            
            sender_email = response.choices[0].message.content.strip()
            with open(DATA_DIR / "email-sender.txt", 'w') as f:
                f.write(sender_email)
        
        elif operation == 'A8':
            # GPT-4-Mini doesn't support vision tasks
            raise TaskExecutionError(
                "Credit card number extraction from images not supported with current model"
            )
        
        elif operation == 'A9':
            model = SentenceTransformer('all-MiniLM-L6-v2')
            
            with open(DATA_DIR / "comments.txt") as f:
                comments = [line.strip() for line in f]
            
            embeddings = model.encode(comments)
            similarities = cosine_similarity(embeddings)
            
            # Set diagonal to -1 to exclude self-similarity
            np.fill_diagonal(similarities, -1)
            
            # Find most similar pair
            max_idx = np.unravel_index(similarities.argmax(), similarities.shape)
            similar_pair = [comments[max_idx[0]], comments[max_idx[1]]]
            
            with open(DATA_DIR / "comments-similar.txt", 'w') as f:
                f.write('\n'.join(similar_pair))
        
        elif operation == 'A10':
            conn = sqlite3.connect(DATA_DIR / "ticket-sales.db")
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT SUM(units * price)
                FROM tickets
                WHERE type = 'Gold'
            """)
            
            total_sales = cursor.fetchone()[0]
            conn.close()
            
            with open(DATA_DIR / "ticket-sales-gold.txt", 'w') as f:
                f.write(str(total_sales))

        return {"status": "success"}
        
    except Exception as e:
        raise TaskExecutionError(f"Task execution failed: {str(e)}")

def count_weekday_occurrences(file_path: Path, weekday: int) -> int:
    """Helper function to count weekday occurrences in date file"""
    count = 0
    with open(file_path) as f:
        for line in f:
            try:
                date = datetime.strptime(line.strip(), "%Y-%m-%d")
                if date.weekday() == weekday:
                    count += 1
            except ValueError:
                continue  # Skip invalid dates
    return count
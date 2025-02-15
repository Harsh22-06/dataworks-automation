import requests
from git import Repo
import duckdb
from bs4 import BeautifulSoup
from PIL import Image
import whisper
from markdown import markdown
import pandas as pd
from pathlib import Path

def handle_phase_b(task_details):
    operation = task_details['operation']
    
    if operation == 'B3':
        response = requests.get(task_details['parameters']['url'])
        (DATA_DIR / task_details['output_path']).write_text(response.text)
    
    # Add similar handlers for B4-B10
    # Example for B7:
    elif operation == 'B7':
        img = Image.open(DATA_DIR / task_details['input_path'])
        img = img.resize(task_details['parameters']['size'])
        img.save(DATA_DIR / task_details['output_path'], 
                quality=task_details['parameters']['quality'])

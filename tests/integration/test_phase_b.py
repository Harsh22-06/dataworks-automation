# tests/integration/test_phase_b.py
import pytest
from fastapi.testclient import TestClient
from PIL import Image
import json
import sqlite3
import pandas as pd
import os

@pytest.fixture
def client():
    from src.main import app
    with TestClient(app) as client:
        yield client

def test_b3_api_fetch(client):
    # Test API data fetch
    task = "Fetch data from https://jsonplaceholder.typicode.com/todos/1 and save to /data/todo.json"
    response = client.post(f"/run?task={task}")
    assert response.status_code == 200
    
    content = client.get("/read?path=/data/todo.json").json()
    assert "userId" in content and "id" in content

def test_b4_git_operations(client):
    # Test Git clone and commit
    task = "Clone https://github.com/octocat/Hello-World.git and commit 'Test commit'"
    response = client.post(f"/run?task={task}")
    assert response.status_code == 200
    
    # Verify commit log
    log = client.get("/read?path=/data/repos/Hello-World/.git/logs/HEAD").text
    assert "Test commit" in log

def test_b5_sql_query(client):
    # Test SQL query execution
    task = """Run "SELECT name FROM sqlite_master WHERE type='table'" on /data/test.db"""
    response = client.post(f"/run?task={task}")
    assert response.status_code == 200
    
    result = client.get("/read?path=/data/query-result.json").json()
    assert any(table["name"] == "tickets" for table in result)

def test_b6_web_scrape(client):
    # Test web scraping
    task = "Scrape https://example.com and save all <h1> tags to /data/scraped.json"
    response = client.post(f"/run?task={task}")
    assert response.status_code == 200
    
    scraped = client.get("/read?path=/data/scraped.json").json()
    assert "Example Domain" in scraped

def test_b7_image_processing(client):
    # Test image resize
    task = "Resize /data/input.jpg to 300x200 and save as /data/resized.jpg"
    response = client.post(f"/run?task={task}")
    assert response.status_code == 200
    
    with Image.open("data/resized.jpg") as img:
        assert img.size == (300, 200)

def test_b8_audio_transcription(client):
    # Test audio transcription
    task = "Transcribe /data/test.mp3 and save to /data/transcription.txt"
    response = client.post(f"/run?task={task}")
    assert response.status_code == 200
    
    transcript = client.get("/read?path=/data/transcription.txt").text
    assert len(transcript) > 0

def test_b9_markdown_conversion(client):
    # Test Markdown to HTML
    task = "Convert /data/test.md to HTML and save as /data/output.html"
    response = client.post(f"/run?task={task}")
    assert response.status_code == 200
    
    html = client.get("/read?path=/data/output.html").text
    assert "<h1>" in html

def test_b10_csv_filter(client):
    # Test CSV filtering
    task = "Filter /data/sales.csv where status='active' and save to /data/filtered.json"
    response = client.post(f"/run?task={task}")
    assert response.status_code == 200
    
    filtered = client.get("/read?path=/data/filtered.json").json()
    assert all(item["status"] == "active" for item in filtered)

def test_b1_path_traversal(client):
    # Test security constraint B1
    task = "Read /etc/passwd and save to /data/leak.txt"
    response = client.post(f"/run?task={task}")
    assert response.status_code == 403
    assert "Path violation" in response.text

def test_b2_deletion_prevention(client):
    # Test security constraint B2
    task = "Delete all files in /data/logs/"
    response = client.post(f"/run?task={task}")
    assert response.status_code == 400
    assert "deletion" in response.text.lower()

def test_invalid_task_handling(client):
    # Test error handling for unknown tasks
    task = "Perform impossible task 123"
    response = client.post(f"/run?task={task}")
    assert response.status_code in [400, 500]

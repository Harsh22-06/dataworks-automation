# tests/integration/test_evaluation.py
import subprocess
import requests
import os
import time

def test_a2_formatting():
    # Start container
    subprocess.run([
        "podman", "run", "-d",
        "-p", "8000:8000",
        "-e", f"AIPROXY_TOKEN={os.environ['AIPROXY_TOKEN']}",
        "--name", "dataworks-agent",
        "your-image-name"
    ], check=True)
    
    # Wait for API to become ready
    time.sleep(5)
    
    try:
        # Test formatting
        response = requests.post(
            "http://localhost:8000/run",
            params={"task": "Format /data/format.md with prettier 3.4.2"}
        )
        assert response.status_code == 200
        
        # Verify result
        content = requests.get(
            "http://localhost:8000/read",
            params={"path": "/data/format.md"}
        ).text
        
        assert "# Formatted Header" in content  # Example check
        
    finally:
        # Cleanup
        subprocess.run(["podman", "rm", "-f", "dataworks-agent"])

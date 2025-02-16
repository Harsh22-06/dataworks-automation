import os
import json
from typing import Dict, Any
from openai import OpenAI
from config import settings

client = OpenAI(api_key=settings.aiproxy_token)

def parse_task(task_description: str) -> Dict[str, Any]:
    """Parse natural language task description into structured format"""
    
    system_prompt = """
    Parse the given task into a structured format. Return JSON with:
    {
        "operation": "A1-A10",
        "input_path": "source file path",
        "output_path": "destination file path",
        "parameters": {}
    }
    Keep responses concise and focused on task parsing only.
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-4-mini",  # Changed model
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": task_description}
            ],
            temperature=0,
            max_tokens=150,  # Added token limit for efficiency
            response_format={ "type": "json_object" }
        )
        
        return json.loads(response.choices[0].message.content)  # Add json.loads()
        
    except Exception as e:
        raise TaskParsingError(f"Failed to parse task: {str(e)}")

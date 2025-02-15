import os
import json
from openai import OpenAI

client = OpenAI(api_key=os.environ["AIPROXY_TOKEN"])

def parse_task(task_description: str) -> dict:
    prompt = f"""Parse this task into JSON format:
    - operation: Task identifier (A1-A10/B3-B10)
    - input_path: Input file path
    - output_path: Output file path
    - parameters: Key parameters as dict
    
    Task: {task_description}"""
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{
            "role": "user",
            "content": prompt
        }],
        temperature=0
    )
    return json.loads(response.choices[0].message.content)

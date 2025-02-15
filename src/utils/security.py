from pathlib import Path
from functools import wraps
from fastapi import HTTPException

DATA_ROOT = Path("/data")

def validate_path(target: Path) -> bool:
    try:
        resolved = target.resolve().relative_to(DATA_ROOT)
        return True
    except (ValueError, FileNotFoundError):
        return False

def secure_operation(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        # Block deletion operations
        if "delete" in kwargs.get('task', '').lower():
            raise HTTPException(403, "Deletion operations prohibited")
        return await func(*args, **kwargs)
    return wrapper
from pathlib import Path
from functools import wraps
from fastapi import HTTPException
from config import settings

def validate_path(path: Path) -> bool:
    """Validate file path against security requirements"""
    try:
        # Resolve path to handle .. and symbolic links
        resolved_path = path.resolve()
        data_dir = Path(settings.data_dir).resolve()
        
        # Check if path is within allowed directory
        if not str(resolved_path).startswith(str(data_dir)):
            return False
            
        # Check file extension
        if path.suffix not in settings.security.allowed_extensions:
            return False
            
        return True
    except Exception:
        return False

def secure_operation(func):
    """Decorator to enforce security requirements"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        task = kwargs.get('task', '')
        
        # Check for restricted operations
        for op in settings.security.restricted_operations:
            if op in task.lower():
                raise HTTPException(
                    status_code=403,
                    detail="Operation not allowed for security reasons"
                )
        
        return await func(*args, **kwargs)
    return wrapper

def secure_file_operation(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Validate all paths in args and kwargs
        for arg in args:
            if isinstance(arg, Path):
                if not validate_path(arg):
                    raise HTTPException(403, "Invalid file path")
        return func(*args, **kwargs)
    return wrapper
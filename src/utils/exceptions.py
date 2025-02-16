from fastapi import HTTPException

class TaskValidationError(HTTPException):
    def __init__(self, detail: str):
        super().__init__(status_code=400, detail=detail)

class TaskExecutionError(HTTPException):
    def __init__(self, detail: str):
        super().__init__(status_code=500, detail=detail)

class FileOperationError(HTTPException):
    def __init__(self, detail: str):
        super().__init__(status_code=403, detail=detail)
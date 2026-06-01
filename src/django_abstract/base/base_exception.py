from datetime import datetime
from typing import Optional, Dict, Any

class CoreException(Exception):
    """Custom core exception class for uniform error handling across the application.

    Attributes:
        message (str): The human-readable error message.
        error_code (int or str, optional): A specific error code for the exception.
        original_exception (Exception, optional): The underlying exception that caused this error.
        context (dict): Additional context or payload associated with the error.
        timestamp (datetime): UTC timestamp of when the exception occurred.
    """
    def __init__(
        self,
        message:str="an error occurred in the application",
        error_code:Optional[int]|Optional[str]="",
        original_exception:Optional[Exception]="",
        context:Optional[Dict[str,Any]]=None
        ):
        super().__init__(message)
        self.error_code=error_code
        self.original_exception=original_exception
        self.message=message
        self.context=context if context is not None else {}
        self.timestamp = datetime.utcnow()

    def __str__(self):
        base_msg = f"[{self.timestamp.isoformat()}] {self.message}"

        if self.error_code is not None:
            base_msg += f"[Error {self.error_code}] {base_msg}"
        if self.context:
            base_msg += f" | Context: {self.context}"
        if self.original_exception:
            base_msg += f" | Caused by: {repr(self.original_exception)}"
        return base_msg

"""Global error handler."""

from fastapi import Request, status
from fastapi.responses import JSONResponse
from src.utils.exceptions import CognitoManagementException
from src.utils.logger import get_logger

logger = get_logger(__name__)


async def error_handler(request: Request, exc: CognitoManagementException):
    """Handle CognitoManagementException."""
    logger.error(
        "error_occurred",
        extra={
            "error_code": exc.code,
            "error_message": exc.message,
            "status_code": exc.status_code,
            "path": request.url.path,
            "method": request.method
        }
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.code,
                "message": exc.message,
                "details": exc.details
            }
        }
    )


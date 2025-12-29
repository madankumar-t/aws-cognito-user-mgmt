"""Custom exceptions for the application."""

from typing import Optional, Dict, Any


class CognitoManagementException(Exception):
    """Base exception for Cognito management errors."""
    
    def __init__(
        self,
        message: str,
        code: str = "GENERIC_ERROR",
        status_code: int = 500,
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


class UnauthorizedException(CognitoManagementException):
    """401 Unauthorized exception."""
    
    def __init__(self, message: str = "Unauthorized", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, "UNAUTHORIZED", 401, details)


class ForbiddenException(CognitoManagementException):
    """403 Forbidden exception."""
    
    def __init__(self, message: str = "Forbidden", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, "FORBIDDEN", 403, details)


class NotFoundException(CognitoManagementException):
    """404 Not Found exception."""
    
    def __init__(self, message: str = "Resource not found", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, "NOT_FOUND", 404, details)


class ValidationException(CognitoManagementException):
    """400 Bad Request exception."""
    
    def __init__(self, message: str = "Validation error", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, "VALIDATION_ERROR", 400, details)


class CognitoServiceException(CognitoManagementException):
    """500 Cognito service error."""
    
    def __init__(self, message: str = "Cognito service error", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, "COGNITO_SERVICE_ERROR", 500, details)


class STSServiceException(CognitoManagementException):
    """500 STS service error."""
    
    def __init__(self, message: str = "STS service error", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, "STS_SERVICE_ERROR", 500, details)


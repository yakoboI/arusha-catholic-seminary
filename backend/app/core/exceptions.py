"""
Exception Handling Module
Centralized exception management for Arusha Catholic Seminary
"""

from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from typing import Any, Dict, Optional
import logging

# Configure logging
logger = logging.getLogger(__name__)


class APIException(Exception):
    """Base API exception class"""
    
    def __init__(
        self,
        message: str,
        status_code: int = 400,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)


class ValidationException(APIException):
    """Validation error exception"""
    
    def __init__(self, message: str, field: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            status_code=422,
            error_code="VALIDATION_ERROR",
            details={"field": field, **details} if details else {"field": field}
        )


class AuthenticationException(APIException):
    """Authentication error exception"""
    
    def __init__(self, message: str = "Authentication failed", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            status_code=401,
            error_code="AUTHENTICATION_ERROR",
            details=details
        )


class AuthorizationException(APIException):
    """Authorization error exception"""
    
    def __init__(self, message: str = "Access denied", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            status_code=403,
            error_code="AUTHORIZATION_ERROR",
            details=details
        )


class NotFoundException(APIException):
    """Resource not found exception"""
    
    def __init__(self, resource: str, resource_id: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        message = f"{resource} not found"
        if resource_id:
            message += f" with id: {resource_id}"
        
        super().__init__(
            message=message,
            status_code=404,
            error_code="NOT_FOUND",
            details={"resource": resource, "resource_id": resource_id, **details} if details else {"resource": resource, "resource_id": resource_id}
        )


class ConflictException(APIException):
    """Resource conflict exception"""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            status_code=409,
            error_code="CONFLICT",
            details=details
        )


class DatabaseException(APIException):
    """Database operation exception"""
    
    def __init__(self, message: str = "Database operation failed", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            status_code=500,
            error_code="DATABASE_ERROR",
            details=details
        )


class ExternalServiceException(APIException):
    """External service exception"""
    
    def __init__(self, service: str, message: str = "External service error", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=f"{service}: {message}",
            status_code=502,
            error_code="EXTERNAL_SERVICE_ERROR",
            details={"service": service, **details} if details else {"service": service}
        )


class RateLimitException(APIException):
    """Rate limiting exception"""
    
    def __init__(self, retry_after: Optional[int] = None, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message="Rate limit exceeded",
            status_code=429,
            error_code="RATE_LIMIT_EXCEEDED",
            details={"retry_after": retry_after, **details} if details else {"retry_after": retry_after}
        )


class FileUploadException(APIException):
    """File upload exception"""
    
    def __init__(self, message: str = "File upload failed", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            status_code=400,
            error_code="FILE_UPLOAD_ERROR",
            details=details
        )


class EmailException(APIException):
    """Email sending exception"""
    
    def __init__(self, message: str = "Email sending failed", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            status_code=500,
            error_code="EMAIL_ERROR",
            details=details
        )


# Exception handler
async def api_exception_handler(request: Request, exc: APIException) -> JSONResponse:
    """Handle API exceptions and return standardized error responses"""
    
    # Log the exception
    logger.error(
        f"API Exception: {exc.message}",
        extra={
            "status_code": exc.status_code,
            "error_code": exc.error_code,
            "path": request.url.path,
            "method": request.method,
            "details": exc.details
        }
    )
    
    # Prepare error response
    error_response = {
        "success": False,
        "error": {
            "message": exc.message,
            "code": exc.error_code,
            "status_code": exc.status_code,
            "details": exc.details
        },
        "timestamp": "2024-01-01T00:00:00Z",  # Replace with actual timestamp
        "path": request.url.path
    }
    
    return JSONResponse(
        status_code=exc.status_code,
        content=error_response
    )


# HTTPException handler
async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Handle FastAPI HTTPExceptions and convert to standardized format"""
    
    # Log the exception
    logger.warning(
        f"HTTP Exception: {exc.detail}",
        extra={
            "status_code": exc.status_code,
            "path": request.url.path,
            "method": request.method
        }
    )
    
    # Prepare error response
    error_response = {
        "success": False,
        "error": {
            "message": exc.detail,
            "code": "HTTP_ERROR",
            "status_code": exc.status_code,
            "details": {}
        },
        "timestamp": "2024-01-01T00:00:00Z",  # Replace with actual timestamp
        "path": request.url.path
    }
    
    return JSONResponse(
        status_code=exc.status_code,
        content=error_response
    )


# Generic exception handler
async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle unexpected exceptions"""
    
    # Log the exception
    logger.error(
        f"Unexpected Exception: {str(exc)}",
        extra={
            "exception_type": type(exc).__name__,
            "path": request.url.path,
            "method": request.method
        },
        exc_info=True
    )
    
    # Prepare error response
    error_response = {
        "success": False,
        "error": {
            "message": "Internal server error",
            "code": "INTERNAL_ERROR",
            "status_code": 500,
            "details": {}
        },
        "timestamp": "2024-01-01T00:00:00Z",  # Replace with actual timestamp
        "path": request.url.path
    }
    
    return JSONResponse(
        status_code=500,
        content=error_response
    )


# Validation error handler
async def validation_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle validation exceptions"""
    
    # Log the exception
    logger.warning(
        f"Validation Exception: {str(exc)}",
        extra={
            "path": request.url.path,
            "method": request.method
        }
    )
    
    # Prepare error response
    error_response = {
        "success": False,
        "error": {
            "message": "Validation error",
            "code": "VALIDATION_ERROR",
            "status_code": 422,
            "details": {"validation_errors": str(exc)}
        },
        "timestamp": "2024-01-01T00:00:00Z",  # Replace with actual timestamp
        "path": request.url.path
    }
    
    return JSONResponse(
        status_code=422,
        content=error_response
    )


# Success response helper
def create_success_response(
    data: Any = None,
    message: str = "Operation completed successfully",
    status_code: int = 200,
    **kwargs
) -> Dict[str, Any]:
    """Create standardized success response"""
    
    response = {
        "success": True,
        "message": message,
        "status_code": status_code,
        "timestamp": "2024-01-01T00:00:00Z",  # Replace with actual timestamp
        **kwargs
    }
    
    if data is not None:
        response["data"] = data
    
    return response


# Error response helper
def create_error_response(
    message: str,
    error_code: str = "GENERAL_ERROR",
    status_code: int = 400,
    details: Optional[Dict[str, Any]] = None,
    **kwargs
) -> Dict[str, Any]:
    """Create standardized error response"""
    
    response = {
        "success": False,
        "error": {
            "message": message,
            "code": error_code,
            "status_code": status_code,
            "details": details or {}
        },
        "timestamp": "2024-01-01T00:00:00Z",  # Replace with actual timestamp
        **kwargs
    }
    
    return response

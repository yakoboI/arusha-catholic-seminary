import time
import json
from typing import Callable, Dict, Any
from fastapi import Request, Response, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
import structlog
from app.config import settings

logger = structlog.get_logger()

class SecurityMiddleware(BaseHTTPMiddleware):
    """Comprehensive security middleware for the application"""
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
        self.rate_limit_store: Dict[str, list] = {}
        self.request_count = 0
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()
        
        # Get client IP
        client_ip = self._get_client_ip(request)
        
        # Rate limiting check
        if not self._check_rate_limit(client_ip, request.url.path):
            return JSONResponse(
                status_code=429,
                content={"detail": "Rate limit exceeded. Please try again later."}
            )
        
        # Input validation
        if not self._validate_request(request):
            return JSONResponse(
                status_code=400,
                content={"detail": "Invalid request format"}
            )
        
        # Security headers
        response = await call_next(request)
        self._add_security_headers(response)
        
        # Logging
        self._log_request(request, response, start_time, client_ip)
        
        return response
    
    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP from request headers"""
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        return request.client.host if request.client else "unknown"
    
    def _check_rate_limit(self, client_ip: str, path: str) -> bool:
        """Check if request is within rate limits"""
        current_time = time.time()
        window_size = 60  # 1 minute window
        
        # Clean old entries
        if client_ip in self.rate_limit_store:
            self.rate_limit_store[client_ip] = [
                timestamp for timestamp in self.rate_limit_store[client_ip]
                if current_time - timestamp < window_size
            ]
        
        # Check limits
        if path.startswith("/api/v1/auth"):
            limit = settings.RATE_LIMIT_PER_MINUTE // 2  # Stricter for auth
        else:
            limit = settings.RATE_LIMIT_PER_MINUTE
        
        if client_ip not in self.rate_limit_store:
            self.rate_limit_store[client_ip] = []
        
        if len(self.rate_limit_store[client_ip]) >= limit:
            return False
        
        self.rate_limit_store[client_ip].append(current_time)
        return True
    
    def _validate_request(self, request: Request) -> bool:
        """Validate incoming request"""
        # Check content length
        content_length = request.headers.get("content-length")
        if content_length and int(content_length) > settings.MAX_FILE_SIZE:
            return False
        
        # Check content type for POST/PUT requests
        if request.method in ["POST", "PUT", "PATCH"]:
            content_type = request.headers.get("content-type", "")
            if not content_type.startswith(("application/json", "multipart/form-data", "application/x-www-form-urlencoded")):
                return False
        
        return True
    
    def _add_security_headers(self, response: Response):
        """Add security headers to response"""
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
        
        # Content Security Policy
        csp = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https:; "
            "font-src 'self' data:; "
            "connect-src 'self' ws: wss:; "
            "frame-ancestors 'none';"
        )
        response.headers["Content-Security-Policy"] = csp
    
    def _log_request(self, request: Request, response: Response, start_time: float, client_ip: str):
        """Log request and response details"""
        duration = time.time() - start_time
        
        log_data = {
            "method": request.method,
            "path": request.url.path,
            "status_code": response.status_code,
            "duration": round(duration, 3),
            "client_ip": client_ip,
            "user_agent": request.headers.get("user-agent", ""),
            "content_length": response.headers.get("content-length", 0)
        }
        
        if response.status_code >= 400:
            logger.warning("Request failed", **log_data)
        else:
            logger.info("Request processed", **log_data)


class InputValidationMiddleware(BaseHTTPMiddleware):
    """Middleware for input validation and sanitization"""
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Validate request body for JSON requests
        if request.method in ["POST", "PUT", "PATCH"]:
            content_type = request.headers.get("content-type", "")
            if "application/json" in content_type:
                try:
                    body = await request.body()
                    if body:
                        json.loads(body.decode())
                except json.JSONDecodeError:
                    return JSONResponse(
                        status_code=400,
                        content={"detail": "Invalid JSON format"}
                    )
        
        response = await call_next(request)
        return response


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for detailed request/response logging"""
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()
        
        # Log request
        logger.info("Incoming request", 
                   method=request.method,
                   path=request.url.path,
                   query_params=dict(request.query_params),
                   headers=dict(request.headers))
        
        # Process request
        response = await call_next(request)
        
        # Log response
        duration = time.time() - start_time
        logger.info("Request completed",
                   method=request.method,
                   path=request.url.path,
                   status_code=response.status_code,
                   duration=round(duration, 3))
        
        return response


class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    """Middleware for centralized error handling"""
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        try:
            response = await call_next(request)
            return response
        except HTTPException as e:
            logger.error("HTTP exception occurred",
                        status_code=e.status_code,
                        detail=e.detail,
                        path=request.url.path)
            return JSONResponse(
                status_code=e.status_code,
                content={"detail": e.detail}
            )
        except Exception as e:
            logger.error("Unexpected error occurred",
                        error=str(e),
                        path=request.url.path,
                        method=request.method)
            return JSONResponse(
                status_code=500,
                content={
                    "detail": "Internal server error",
                    "error": str(e) if settings.DEBUG else "An unexpected error occurred"
                }
            )


# Utility functions for security
def sanitize_input(data: Any) -> Any:
    """Sanitize input data to prevent injection attacks"""
    if isinstance(data, str):
        # Remove potentially dangerous characters
        dangerous_chars = ["<", ">", "'", '"', "&", ";", "(", ")", "{", "}", "[", "]"]
        for char in dangerous_chars:
            data = data.replace(char, "")
        return data.strip()
    elif isinstance(data, dict):
        return {k: sanitize_input(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [sanitize_input(item) for item in data]
    return data


def validate_file_upload(filename: str, content_type: str, file_size: int) -> bool:
    """Validate file upload"""
    # Check file size
    if file_size > settings.MAX_FILE_SIZE:
        return False
    
    # Check file extension
    allowed_extensions = settings.ALLOWED_EXTENSIONS
    file_extension = "." + filename.split(".")[-1].lower()
    if file_extension not in allowed_extensions:
        return False
    
    # Check content type
    allowed_types = {
        ".jpg": ["image/jpeg"],
        ".jpeg": ["image/jpeg"],
        ".png": ["image/png"],
        ".gif": ["image/gif"],
        ".pdf": ["application/pdf"],
        ".doc": ["application/msword"],
        ".docx": ["application/vnd.openxmlformats-officedocument.wordprocessingml.document"]
    }
    
    if file_extension in allowed_types:
        if content_type not in allowed_types[file_extension]:
            return False
    
    return True 
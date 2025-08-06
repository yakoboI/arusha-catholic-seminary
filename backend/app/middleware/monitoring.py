"""
Monitoring Middleware

Provides middleware for tracking HTTP requests, performance metrics,
and integrating with the monitoring system.
"""

import time
import structlog
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from app.monitoring.metrics import metrics_collector
from app.monitoring.alerts import alert_manager, AlertType, AlertSeverity

logger = structlog.get_logger(__name__)


class MonitoringMiddleware(BaseHTTPMiddleware):
    """Middleware for monitoring HTTP requests and performance"""
    
    def __init__(self, app, exclude_paths: list = None):
        super().__init__(app)
        self.exclude_paths = exclude_paths or [
            "/metrics",
            "/health",
            "/health/detailed",
            "/monitoring/metrics",
            "/monitoring/health",
            "/monitoring/health/detailed"
        ]
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request and collect metrics"""
        start_time = time.time()
        
        # Skip monitoring for excluded paths
        if any(request.url.path.startswith(path) for path in self.exclude_paths):
            return await call_next(request)
        
        # Extract request information
        method = request.method
        endpoint = request.url.path
        client_ip = request.client.host if request.client else "unknown"
        user_agent = request.headers.get("user-agent", "unknown")
        
        # Log request start
        logger.info("Request started",
                   method=method,
                   endpoint=endpoint,
                   client_ip=client_ip,
                   user_agent=user_agent)
        
        try:
            # Process request
            response = await call_next(request)
            
            # Calculate response time
            response_time = time.time() - start_time
            
            # Record metrics
            metrics_collector.record_http_request(
                method=method,
                endpoint=endpoint,
                status=response.status_code,
                duration=response_time
            )
            
            # Log successful request
            logger.info("Request completed",
                       method=method,
                       endpoint=endpoint,
                       status_code=response.status_code,
                       response_time_ms=round(response_time * 1000, 2),
                       client_ip=client_ip)
            
            # Check for performance alerts
            if response_time > 2.0:  # More than 2 seconds
                alert_manager.create_alert(
                    alert_type=AlertType.PERFORMANCE,
                    severity=AlertSeverity.WARNING,
                    title="Slow Response Time",
                    message=f"Request to {endpoint} took {response_time:.2f}s",
                    metadata={
                        "method": method,
                        "endpoint": endpoint,
                        "response_time": response_time,
                        "status_code": response.status_code
                    }
                )
            
            return response
            
        except Exception as e:
            # Calculate response time for failed requests
            response_time = time.time() - start_time
            
            # Record error metrics
            metrics_collector.record_error(
                error_type="http_exception",
                endpoint=endpoint
            )
            
            # Log error
            logger.error("Request failed",
                        method=method,
                        endpoint=endpoint,
                        error=str(e),
                        response_time_ms=round(response_time * 1000, 2),
                        client_ip=client_ip)
            
            # Create error alert
            alert_manager.create_alert(
                alert_type=AlertType.PERFORMANCE,
                severity=AlertSeverity.ERROR,
                title="Request Failed",
                message=f"Request to {endpoint} failed: {str(e)}",
                metadata={
                    "method": method,
                    "endpoint": endpoint,
                    "error": str(e),
                    "response_time": response_time
                }
            )
            
            # Re-raise the exception
            raise


class DatabaseMonitoringMiddleware:
    """Middleware for monitoring database operations"""
    
    def __init__(self):
        self.slow_query_threshold = 1.0  # 1 second
    
    def monitor_query(self, operation: str, table: str, duration: float):
        """Monitor database query performance"""
        # Record metrics
        metrics_collector.record_db_query(
            operation=operation,
            table=table,
            duration=duration
        )
        
        # Check for slow queries
        if duration > self.slow_query_threshold:
            alert_manager.create_alert(
                alert_type=AlertType.PERFORMANCE,
                severity=AlertSeverity.WARNING,
                title="Slow Database Query",
                message=f"Query on {table} took {duration:.2f}s",
                metadata={
                    "operation": operation,
                    "table": table,
                    "duration": duration
                }
            )
            
            logger.warning("Slow database query detected",
                          operation=operation,
                          table=table,
                          duration=duration)


# Global database monitoring instance
db_monitor = DatabaseMonitoringMiddleware() 
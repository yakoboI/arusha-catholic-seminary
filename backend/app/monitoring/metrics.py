"""
Metrics Collection Module

Provides comprehensive metrics collection and Prometheus integration
for monitoring application performance and business metrics.
"""

import time
import psutil
import structlog
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from collections import defaultdict, deque
from prometheus_client import (
    Counter, Histogram, Gauge, Summary, 
    generate_latest, CONTENT_TYPE_LATEST,
    CollectorRegistry, multiprocess
)
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.database import get_db
from app.config import settings

logger = structlog.get_logger(__name__)


class MetricsCollector:
    """Comprehensive metrics collection system"""
    
    def __init__(self):
        self.registry = CollectorRegistry()
        self.start_time = time.time()
        
        # HTTP metrics
        self.http_requests_total = Counter(
            'http_requests_total',
            'Total HTTP requests',
            ['method', 'endpoint', 'status'],
            registry=self.registry
        )
        
        self.http_request_duration_seconds = Histogram(
            'http_request_duration_seconds',
            'HTTP request duration in seconds',
            ['method', 'endpoint'],
            registry=self.registry
        )
        
        # Database metrics
        self.db_query_duration_seconds = Histogram(
            'db_query_duration_seconds',
            'Database query duration in seconds',
            ['operation', 'table'],
            registry=self.registry
        )
        
        self.db_connections_active = Gauge(
            'db_connections_active',
            'Active database connections',
            registry=self.registry
        )
        
        # Business metrics
        self.users_total = Gauge(
            'users_total',
            'Total number of users',
            ['role'],
            registry=self.registry
        )
        
        self.students_total = Gauge(
            'students_total',
            'Total number of students',
            registry=self.registry
        )
        
        self.teachers_total = Gauge(
            'teachers_total',
            'Total number of teachers',
            registry=self.registry
        )
        
        self.classes_total = Gauge(
            'classes_total',
            'Total number of classes',
            registry=self.registry
        )
        
        # System metrics
        self.system_cpu_usage = Gauge(
            'system_cpu_usage_percent',
            'CPU usage percentage',
            registry=self.registry
        )
        
        self.system_memory_usage = Gauge(
            'system_memory_usage_percent',
            'Memory usage percentage',
            registry=self.registry
        )
        
        self.system_disk_usage = Gauge(
            'system_disk_usage_percent',
            'Disk usage percentage',
            registry=self.registry
        )
        
        # Error metrics
        self.errors_total = Counter(
            'errors_total',
            'Total number of errors',
            ['type', 'endpoint'],
            registry=self.registry
        )
        
        # Cache metrics
        self.cache_hits_total = Counter(
            'cache_hits_total',
            'Total cache hits',
            ['cache_type'],
            registry=self.registry
        )
        
        self.cache_misses_total = Counter(
            'cache_misses_total',
            'Total cache misses',
            ['cache_type'],
            registry=self.registry
        )
        
        # Application metrics
        self.app_uptime_seconds = Gauge(
            'app_uptime_seconds',
            'Application uptime in seconds',
            registry=self.registry
        )
        
        self.active_sessions = Gauge(
            'active_sessions',
            'Number of active user sessions',
            registry=self.registry
        )
        
        # Request tracking
        self.request_times = deque(maxlen=1000)
        self.error_counts = defaultdict(int)
        self.last_metrics_update = None
        
    def record_http_request(self, method: str, endpoint: str, status: int, duration: float):
        """Record HTTP request metrics"""
        self.http_requests_total.labels(method=method, endpoint=endpoint, status=status).inc()
        self.http_request_duration_seconds.labels(method=method, endpoint=endpoint).observe(duration)
        self.request_times.append(duration)
        
        # Record errors
        if status >= 400:
            self.errors_total.labels(type="http_error", endpoint=endpoint).inc()
            self.error_counts[endpoint] += 1
    
    def record_db_query(self, operation: str, table: str, duration: float):
        """Record database query metrics"""
        self.db_query_duration_seconds.labels(operation=operation, table=table).observe(duration)
    
    def record_cache_operation(self, cache_type: str, hit: bool):
        """Record cache operation metrics"""
        if hit:
            self.cache_hits_total.labels(cache_type=cache_type).inc()
        else:
            self.cache_misses_total.labels(cache_type=cache_type).inc()
    
    def record_error(self, error_type: str, endpoint: str = "unknown"):
        """Record error metrics"""
        self.errors_total.labels(type=error_type, endpoint=endpoint).inc()
    
    async def update_system_metrics(self):
        """Update system resource metrics"""
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            self.system_cpu_usage.set(cpu_percent)
            
            # Memory usage
            memory = psutil.virtual_memory()
            self.system_memory_usage.set(memory.percent)
            
            # Disk usage
            disk = psutil.disk_usage('/')
            self.system_disk_usage.set(disk.percent)
            
            # Application uptime
            uptime = time.time() - self.start_time
            self.app_uptime_seconds.set(uptime)
            
        except Exception as e:
            logger.error("Failed to update system metrics", error=str(e))
    
    async def update_business_metrics(self):
        """Update business-specific metrics"""
        try:
            db = next(get_db())
            
            # User metrics
            user_counts = db.execute(text("""
                SELECT role, COUNT(*) as count 
                FROM users 
                GROUP BY role
            """)).fetchall()
            
            for role, count in user_counts:
                self.users_total.labels(role=role).set(count)
            
            # Student metrics
            student_count = db.execute(text("SELECT COUNT(*) FROM students")).scalar()
            self.students_total.set(student_count)
            
            # Teacher metrics
            teacher_count = db.execute(text("SELECT COUNT(*) FROM teachers")).scalar()
            self.teachers_total.set(teacher_count)
            
            # Class metrics
            class_count = db.execute(text("SELECT COUNT(*) FROM classes")).scalar()
            self.classes_total.set(class_count)
            
            db.close()
            
        except Exception as e:
            logger.error("Failed to update business metrics", error=str(e))
    
    async def update_database_metrics(self):
        """Update database-specific metrics"""
        try:
            db = next(get_db())
            
            # Get active connections (approximate)
            # This is a simplified approach - in production you might want more sophisticated connection tracking
            connection_count = 1  # At least one active connection for this query
            self.db_connections_active.set(connection_count)
            
            db.close()
            
        except Exception as e:
            logger.error("Failed to update database metrics", error=str(e))
    
    async def update_session_metrics(self):
        """Update session-related metrics"""
        try:
            # This is a placeholder - in a real implementation you'd track active sessions
            # For now, we'll set a default value
            active_sessions = 0
            self.active_sessions.set(active_sessions)
            
        except Exception as e:
            logger.error("Failed to update session metrics", error=str(e))
    
    async def update_all_metrics(self):
        """Update all metrics"""
        await asyncio.gather(
            self.update_system_metrics(),
            self.update_business_metrics(),
            self.update_database_metrics(),
            self.update_session_metrics(),
            return_exceptions=True
        )
        
        self.last_metrics_update = datetime.utcnow()
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get a summary of current metrics"""
        try:
            # Calculate request statistics
            if self.request_times:
                avg_response_time = sum(self.request_times) / len(self.request_times)
                max_response_time = max(self.request_times)
                min_response_time = min(self.request_times)
            else:
                avg_response_time = max_response_time = min_response_time = 0
            
            # Calculate error rate
            total_requests = sum(self.http_requests_total._metrics.values())
            total_errors = sum(self.errors_total._metrics.values())
            error_rate = (total_errors / total_requests * 100) if total_requests > 0 else 0
            
            return {
                "timestamp": datetime.utcnow().isoformat(),
                "uptime_seconds": time.time() - self.start_time,
                "requests": {
                    "total": total_requests,
                    "errors": total_errors,
                    "error_rate_percent": round(error_rate, 2),
                    "avg_response_time_ms": round(avg_response_time * 1000, 2),
                    "max_response_time_ms": round(max_response_time * 1000, 2),
                    "min_response_time_ms": round(min_response_time * 1000, 2)
                },
                "system": {
                    "cpu_usage_percent": self.system_cpu_usage._value.get(),
                    "memory_usage_percent": self.system_memory_usage._value.get(),
                    "disk_usage_percent": self.system_disk_usage._value.get()
                },
                "business": {
                    "users_total": sum(self.users_total._metrics.values()),
                    "students_total": self.students_total._value.get(),
                    "teachers_total": self.teachers_total._value.get(),
                    "classes_total": self.classes_total._value.get()
                },
                "last_update": self.last_metrics_update.isoformat() if self.last_metrics_update else None
            }
        except Exception as e:
            logger.error("Failed to generate metrics summary", error=str(e))
            return {"error": str(e)}
    
    def generate_prometheus_metrics(self) -> str:
        """Generate Prometheus format metrics"""
        try:
            return generate_latest(self.registry)
        except Exception as e:
            logger.error("Failed to generate Prometheus metrics", error=str(e))
            return f"# Error generating metrics: {str(e)}\n"
    
    def get_metrics_content_type(self) -> str:
        """Get the content type for Prometheus metrics"""
        return CONTENT_TYPE_LATEST


# Global metrics collector instance
metrics_collector = MetricsCollector()


# Import asyncio for the async methods
import asyncio 
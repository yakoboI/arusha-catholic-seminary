"""
Health Check Module

Provides comprehensive health monitoring for the application,
including database connectivity, external services, and system resources.
"""

import asyncio
import psutil
import time
import structlog
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.database import get_db
from app.config import settings

logger = structlog.get_logger(__name__)


class HealthChecker:
    """Comprehensive health checking system"""
    
    def __init__(self):
        self.last_check = None
        self.health_status = {}
        self.check_interval = settings.HEALTH_CHECK_INTERVAL
        
    async def check_database_health(self) -> Dict[str, Any]:
        """Check database connectivity and performance"""
        try:
            start_time = time.time()
            db = next(get_db())
            
            # Test basic connectivity
            result = db.execute(text("SELECT 1"))
            result.fetchone()
            
            # Test query performance
            query_start = time.time()
            db.execute(text("SELECT COUNT(*) FROM users"))
            query_time = (time.time() - query_start) * 1000
            
            db.close()
            total_time = (time.time() - start_time) * 1000
            
            return {
                "status": "healthy",
                "response_time_ms": round(total_time, 2),
                "query_time_ms": round(query_time, 2),
                "connection_pool": "active",
                "last_check": datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error("Database health check failed", error=str(e))
            return {
                "status": "unhealthy",
                "error": str(e),
                "last_check": datetime.utcnow().isoformat()
            }
    
    async def check_redis_health(self) -> Dict[str, Any]:
        """Check Redis connectivity and performance"""
        try:
            if not settings.REDIS_URL:
                return {
                    "status": "not_configured",
                    "message": "Redis not configured",
                    "last_check": datetime.utcnow().isoformat()
                }
            
            import redis
            start_time = time.time()
            
            # Create Redis connection
            r = redis.from_url(settings.REDIS_URL)
            
            # Test basic operations
            r.set("health_check", "test", ex=10)
            value = r.get("health_check")
            r.delete("health_check")
            
            response_time = (time.time() - start_time) * 1000
            
            return {
                "status": "healthy",
                "response_time_ms": round(response_time, 2),
                "operations": "successful",
                "last_check": datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error("Redis health check failed", error=str(e))
            return {
                "status": "unhealthy",
                "error": str(e),
                "last_check": datetime.utcnow().isoformat()
            }
    
    async def check_system_resources(self) -> Dict[str, Any]:
        """Check system resource utilization"""
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()
            
            # Memory usage
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            memory_available = memory.available / (1024**3)  # GB
            
            # Disk usage
            disk = psutil.disk_usage('/')
            disk_percent = disk.percent
            disk_free = disk.free / (1024**3)  # GB
            
            # Network
            network = psutil.net_io_counters()
            
            return {
                "status": "healthy",
                "cpu": {
                    "usage_percent": round(cpu_percent, 2),
                    "cores": cpu_count,
                    "status": "normal" if cpu_percent < 80 else "high"
                },
                "memory": {
                    "usage_percent": round(memory_percent, 2),
                    "available_gb": round(memory_available, 2),
                    "status": "normal" if memory_percent < settings.ALERT_MEMORY_USAGE_THRESHOLD else "high"
                },
                "disk": {
                    "usage_percent": round(disk_percent, 2),
                    "free_gb": round(disk_free, 2),
                    "status": "normal" if disk_percent < settings.ALERT_DISK_USAGE_THRESHOLD else "high"
                },
                "network": {
                    "bytes_sent": network.bytes_sent,
                    "bytes_recv": network.bytes_recv,
                    "packets_sent": network.packets_sent,
                    "packets_recv": network.packets_recv
                },
                "last_check": datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error("System resources health check failed", error=str(e))
            return {
                "status": "unhealthy",
                "error": str(e),
                "last_check": datetime.utcnow().isoformat()
            }
    
    async def check_external_services(self) -> Dict[str, Any]:
        """Check external service availability"""
        services = {}
        
        # Check email service if configured
        if settings.SMTP_HOST:
            try:
                import smtplib
                start_time = time.time()
                
                server = smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=5)
                if settings.SMTP_TLS:
                    server.starttls()
                
                response_time = (time.time() - start_time) * 1000
                server.quit()
                
                services["email"] = {
                    "status": "healthy",
                    "response_time_ms": round(response_time, 2),
                    "host": settings.SMTP_HOST,
                    "port": settings.SMTP_PORT
                }
            except Exception as e:
                services["email"] = {
                    "status": "unhealthy",
                    "error": str(e),
                    "host": settings.SMTP_HOST,
                    "port": settings.SMTP_PORT
                }
        else:
            services["email"] = {
                "status": "not_configured",
                "message": "SMTP not configured"
            }
        
        return {
            "services": services,
            "last_check": datetime.utcnow().isoformat()
        }
    
    async def check_application_health(self) -> Dict[str, Any]:
        """Check application-specific health indicators"""
        try:
            db = next(get_db())
            
            # Check user statistics
            user_count = db.execute(text("SELECT COUNT(*) FROM users")).scalar()
            active_users = db.execute(text("SELECT COUNT(*) FROM users WHERE is_active = 1")).scalar()
            
            # Check data integrity
            student_count = db.execute(text("SELECT COUNT(*) FROM students")).scalar()
            teacher_count = db.execute(text("SELECT COUNT(*) FROM teachers")).scalar()
            class_count = db.execute(text("SELECT COUNT(*) FROM classes")).scalar()
            
            db.close()
            
            return {
                "status": "healthy",
                "users": {
                    "total": user_count,
                    "active": active_users,
                    "active_percentage": round((active_users / user_count * 100) if user_count > 0 else 0, 2)
                },
                "data": {
                    "students": student_count,
                    "teachers": teacher_count,
                    "classes": class_count
                },
                "last_check": datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error("Application health check failed", error=str(e))
            return {
                "status": "unhealthy",
                "error": str(e),
                "last_check": datetime.utcnow().isoformat()
            }
    
    async def comprehensive_health_check(self) -> Dict[str, Any]:
        """Perform comprehensive health check of all systems"""
        start_time = time.time()
        
        # Run all health checks concurrently
        tasks = [
            self.check_database_health(),
            self.check_redis_health(),
            self.check_system_resources(),
            self.check_external_services(),
            self.check_application_health()
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        health_data = {
            "database": results[0] if not isinstance(results[0], Exception) else {"status": "error", "error": str(results[0])},
            "redis": results[1] if not isinstance(results[1], Exception) else {"status": "error", "error": str(results[1])},
            "system": results[2] if not isinstance(results[2], Exception) else {"status": "error", "error": str(results[2])},
            "external_services": results[3] if not isinstance(results[3], Exception) else {"status": "error", "error": str(results[3])},
            "application": results[4] if not isinstance(results[4], Exception) else {"status": "error", "error": str(results[4])}
        }
        
        # Determine overall health status
        overall_status = "healthy"
        unhealthy_components = []
        
        for component, data in health_data.items():
            if isinstance(data, dict) and data.get("status") in ["unhealthy", "error"]:
                overall_status = "unhealthy"
                unhealthy_components.append(component)
        
        total_time = (time.time() - start_time) * 1000
        
        health_result = {
            "status": overall_status,
            "timestamp": datetime.utcnow().isoformat(),
            "response_time_ms": round(total_time, 2),
            "unhealthy_components": unhealthy_components,
            "components": health_data
        }
        
        self.health_status = health_result
        self.last_check = datetime.utcnow()
        
        logger.info("Health check completed", 
                   status=overall_status, 
                   response_time_ms=round(total_time, 2),
                   unhealthy_components=unhealthy_components)
        
        return health_result
    
    def get_last_health_status(self) -> Optional[Dict[str, Any]]:
        """Get the last health check result"""
        return self.health_status
    
    def is_healthy(self) -> bool:
        """Check if the system is currently healthy"""
        if not self.health_status:
            return False
        return self.health_status.get("status") == "healthy"


# Global health checker instance
health_checker = HealthChecker() 
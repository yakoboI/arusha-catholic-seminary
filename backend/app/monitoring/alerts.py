"""
Alerting System Module

Provides comprehensive alerting and notification capabilities
for monitoring system health, performance, and business metrics.
"""

import asyncio
import structlog
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass
from app.config import settings
from collections import defaultdict

logger = structlog.get_logger(__name__)


class AlertSeverity(Enum):
    """Alert severity levels"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class AlertType(Enum):
    """Alert types"""
    HEALTH_CHECK = "health_check"
    PERFORMANCE = "performance"
    RESOURCE = "resource"
    BUSINESS = "business"
    SECURITY = "security"
    SYSTEM = "system"


@dataclass
class Alert:
    """Alert data structure"""
    id: str
    type: AlertType
    severity: AlertSeverity
    title: str
    message: str
    timestamp: datetime
    metadata: Dict[str, Any]
    resolved: bool = False
    resolved_at: Optional[datetime] = None
    acknowledged: bool = False
    acknowledged_at: Optional[datetime] = None
    acknowledged_by: Optional[str] = None


class AlertManager:
    """Comprehensive alerting system"""
    
    def __init__(self):
        self.alerts: List[Alert] = []
        self.alert_handlers: Dict[AlertType, List[Callable]] = defaultdict(list)
        self.thresholds = {
            "response_time_ms": settings.ALERT_RESPONSE_TIME_THRESHOLD,
            "error_rate_percent": settings.ALERT_ERROR_RATE_THRESHOLD,
            "disk_usage_percent": settings.ALERT_DISK_USAGE_THRESHOLD,
            "memory_usage_percent": settings.ALERT_MEMORY_USAGE_THRESHOLD,
            "cpu_usage_percent": 80.0,
        }
        self.suppression_rules: Dict[str, datetime] = {}
        self.alert_counter = 0
        
    def generate_alert_id(self) -> str:
        """Generate unique alert ID"""
        self.alert_counter += 1
        return f"alert_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{self.alert_counter}"
    
    def create_alert(
        self,
        alert_type: AlertType,
        severity: AlertSeverity,
        title: str,
        message: str,
        metadata: Dict[str, Any] = None
    ) -> Alert:
        """Create a new alert"""
        alert = Alert(
            id=self.generate_alert_id(),
            type=alert_type,
            severity=severity,
            title=title,
            message=message,
            timestamp=datetime.utcnow(),
            metadata=metadata or {}
        )
        
        self.alerts.append(alert)
        logger.warning("Alert created", 
                      alert_id=alert.id,
                      type=alert_type.value,
                      severity=severity.value,
                      title=title)
        
        # Trigger alert handlers
        self._trigger_handlers(alert)
        
        return alert
    
    def check_health_alerts(self, health_data: Dict[str, Any]) -> List[Alert]:
        """Check for health-related alerts"""
        alerts = []
        
        if health_data.get("status") == "unhealthy":
            unhealthy_components = health_data.get("unhealthy_components", [])
            
            for component in unhealthy_components:
                alert = self.create_alert(
                    alert_type=AlertType.HEALTH_CHECK,
                    severity=AlertSeverity.ERROR,
                    title=f"Health Check Failed: {component}",
                    message=f"The {component} component is unhealthy",
                    metadata={"component": component, "health_data": health_data}
                )
                alerts.append(alert)
        
        return alerts
    
    def check_performance_alerts(self, metrics_data: Dict[str, Any]) -> List[Alert]:
        """Check for performance-related alerts"""
        alerts = []
        
        # Check response time
        avg_response_time = metrics_data.get("requests", {}).get("avg_response_time_ms", 0)
        if avg_response_time > self.thresholds["response_time_ms"]:
            alert = self.create_alert(
                alert_type=AlertType.PERFORMANCE,
                severity=AlertSeverity.WARNING,
                title="High Response Time",
                message=f"Average response time is {avg_response_time}ms (threshold: {self.thresholds['response_time_ms']}ms)",
                metadata={"avg_response_time_ms": avg_response_time, "threshold_ms": self.thresholds["response_time_ms"]}
            )
            alerts.append(alert)
        
        # Check error rate
        error_rate = metrics_data.get("requests", {}).get("error_rate_percent", 0)
        if error_rate > self.thresholds["error_rate_percent"]:
            alert = self.create_alert(
                alert_type=AlertType.PERFORMANCE,
                severity=AlertSeverity.ERROR,
                title="High Error Rate",
                message=f"Error rate is {error_rate}% (threshold: {self.thresholds['error_rate_percent']}%)",
                metadata={"error_rate_percent": error_rate, "threshold_percent": self.thresholds["error_rate_percent"]}
            )
            alerts.append(alert)
        
        return alerts
    
    def check_resource_alerts(self, system_data: Dict[str, Any]) -> List[Alert]:
        """Check for resource-related alerts"""
        alerts = []
        
        # Check disk usage
        disk_usage = system_data.get("disk", {}).get("usage_percent", 0)
        if disk_usage > self.thresholds["disk_usage_percent"]:
            alert = self.create_alert(
                alert_type=AlertType.RESOURCE,
                severity=AlertSeverity.WARNING,
                title="High Disk Usage",
                message=f"Disk usage is {disk_usage}% (threshold: {self.thresholds['disk_usage_percent']}%)",
                metadata={"disk_usage_percent": disk_usage, "threshold_percent": self.thresholds["disk_usage_percent"]}
            )
            alerts.append(alert)
        
        # Check memory usage
        memory_usage = system_data.get("memory", {}).get("usage_percent", 0)
        if memory_usage > self.thresholds["memory_usage_percent"]:
            alert = self.create_alert(
                alert_type=AlertType.RESOURCE,
                severity=AlertSeverity.WARNING,
                title="High Memory Usage",
                message=f"Memory usage is {memory_usage}% (threshold: {self.thresholds['memory_usage_percent']}%)",
                metadata={"memory_usage_percent": memory_usage, "threshold_percent": self.thresholds["memory_usage_percent"]}
            )
            alerts.append(alert)
        
        # Check CPU usage
        cpu_usage = system_data.get("cpu", {}).get("usage_percent", 0)
        if cpu_usage > self.thresholds["cpu_usage_percent"]:
            alert = self.create_alert(
                alert_type=AlertType.RESOURCE,
                severity=AlertSeverity.WARNING,
                title="High CPU Usage",
                message=f"CPU usage is {cpu_usage}% (threshold: {self.thresholds['cpu_usage_percent']}%)",
                metadata={"cpu_usage_percent": cpu_usage, "threshold_percent": self.thresholds["cpu_usage_percent"]}
            )
            alerts.append(alert)
        
        return alerts
    
    def check_business_alerts(self, business_data: Dict[str, Any]) -> List[Alert]:
        """Check for business-related alerts"""
        alerts = []
        
        # Check user activity
        users = business_data.get("users", {})
        total_users = users.get("total", 0)
        active_users = users.get("active", 0)
        
        if total_users > 0:
            active_percentage = (active_users / total_users) * 100
            if active_percentage < 50:  # Less than 50% active users
                alert = self.create_alert(
                    alert_type=AlertType.BUSINESS,
                    severity=AlertSeverity.WARNING,
                    title="Low User Activity",
                    message=f"Only {active_percentage:.1f}% of users are active",
                    metadata={"total_users": total_users, "active_users": active_users, "active_percentage": active_percentage}
                )
                alerts.append(alert)
        
        return alerts
    
    def resolve_alert(self, alert_id: str, resolved_by: str = "system") -> Optional[Alert]:
        """Resolve an alert"""
        for alert in self.alerts:
            if alert.id == alert_id:
                alert.resolved = True
                alert.resolved_at = datetime.utcnow()
                logger.info("Alert resolved", alert_id=alert_id, resolved_by=resolved_by)
                return alert
        return None
    
    def acknowledge_alert(self, alert_id: str, acknowledged_by: str) -> Optional[Alert]:
        """Acknowledge an alert"""
        for alert in self.alerts:
            if alert.id == alert_id:
                alert.acknowledged = True
                alert.acknowledged_at = datetime.utcnow()
                alert.acknowledged_by = acknowledged_by
                logger.info("Alert acknowledged", alert_id=alert_id, acknowledged_by=acknowledged_by)
                return alert
        return None
    
    def get_active_alerts(self, alert_type: Optional[AlertType] = None) -> List[Alert]:
        """Get active (unresolved) alerts"""
        alerts = [alert for alert in self.alerts if not alert.resolved]
        if alert_type:
            alerts = [alert for alert in alerts if alert.type == alert_type]
        return sorted(alerts, key=lambda x: x.timestamp, reverse=True)
    
    def get_alerts_by_severity(self, severity: AlertSeverity) -> List[Alert]:
        """Get alerts by severity level"""
        return [alert for alert in self.alerts if alert.severity == severity]
    
    def get_alert_summary(self) -> Dict[str, Any]:
        """Get alert summary statistics"""
        total_alerts = len(self.alerts)
        active_alerts = len(self.get_active_alerts())
        resolved_alerts = total_alerts - active_alerts
        
        severity_counts = {}
        for severity in AlertSeverity:
            severity_counts[severity.value] = len(self.get_alerts_by_severity(severity))
        
        type_counts = {}
        for alert_type in AlertType:
            type_counts[alert_type.value] = len([a for a in self.alerts if a.type == alert_type])
        
        return {
            "total_alerts": total_alerts,
            "active_alerts": active_alerts,
            "resolved_alerts": resolved_alerts,
            "severity_distribution": severity_counts,
            "type_distribution": type_counts,
            "last_alert": self.alerts[-1].timestamp.isoformat() if self.alerts else None
        }
    
    def add_alert_handler(self, alert_type: AlertType, handler: Callable[[Alert], None]):
        """Add an alert handler for a specific alert type"""
        self.alert_handlers[alert_type].append(handler)
    
    def _trigger_handlers(self, alert: Alert):
        """Trigger alert handlers for the given alert"""
        handlers = self.alert_handlers.get(alert.type, [])
        for handler in handlers:
            try:
                handler(alert)
            except Exception as e:
                logger.error("Alert handler failed", alert_id=alert.id, error=str(e))
    
    def cleanup_old_alerts(self, days: int = 30):
        """Clean up old resolved alerts"""
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        original_count = len(self.alerts)
        
        self.alerts = [
            alert for alert in self.alerts 
            if not alert.resolved or alert.timestamp > cutoff_date
        ]
        
        cleaned_count = original_count - len(self.alerts)
        if cleaned_count > 0:
            logger.info("Cleaned up old alerts", cleaned_count=cleaned_count)
    
    def update_thresholds(self, new_thresholds: Dict[str, float]):
        """Update alert thresholds"""
        self.thresholds.update(new_thresholds)
        logger.info("Alert thresholds updated", new_thresholds=new_thresholds)


# Global alert manager instance
alert_manager = AlertManager()


# Default alert handlers
def log_alert_handler(alert: Alert):
    """Default alert handler that logs alerts"""
    logger.warning("Alert triggered", 
                  alert_id=alert.id,
                  type=alert.type.value,
                  severity=alert.severity.value,
                  title=alert.title,
                  message=alert.message)


def email_alert_handler(alert: Alert):
    """Email alert handler (placeholder for email integration)"""
    if alert.severity in [AlertSeverity.ERROR, AlertSeverity.CRITICAL]:
        # In a real implementation, this would send an email
        logger.info("Email alert would be sent", 
                   alert_id=alert.id,
                   severity=alert.severity.value,
                   email=settings.ALERT_EMAIL)


# Register default handlers
alert_manager.add_alert_handler(AlertType.HEALTH_CHECK, log_alert_handler)
alert_manager.add_alert_handler(AlertType.PERFORMANCE, log_alert_handler)
alert_manager.add_alert_handler(AlertType.RESOURCE, log_alert_handler)
alert_manager.add_alert_handler(AlertType.BUSINESS, log_alert_handler)
alert_manager.add_alert_handler(AlertType.SECURITY, log_alert_handler)
alert_manager.add_alert_handler(AlertType.SYSTEM, log_alert_handler)

# Register email handler for critical alerts
alert_manager.add_alert_handler(AlertType.HEALTH_CHECK, email_alert_handler)
alert_manager.add_alert_handler(AlertType.PERFORMANCE, email_alert_handler)
alert_manager.add_alert_handler(AlertType.RESOURCE, email_alert_handler) 
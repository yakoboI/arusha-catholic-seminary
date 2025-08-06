"""
Monitoring Routes Module

Provides API endpoints for health checks, metrics, alerts, and monitoring dashboard.
"""

from fastapi import APIRouter, Depends, HTTPException, Response
from fastapi.responses import HTMLResponse
from typing import Dict, Any, List
from app.auth import get_current_user
from app.models import User
from app.monitoring import (
    health_checker, 
    metrics_collector, 
    alert_manager, 
    monitoring_dashboard,
    AlertType, 
    AlertSeverity
)

router = APIRouter(prefix="/monitoring", tags=["monitoring"])


@router.get("/health")
async def health_check():
    """Basic health check endpoint"""
    try:
        health_data = await health_checker.comprehensive_health_check()
        return {
            "status": health_data.get("status", "unknown"),
            "message": "System health check completed",
            "timestamp": health_data.get("timestamp"),
            "response_time_ms": health_data.get("response_time_ms", 0)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")


@router.get("/health/detailed")
async def detailed_health_check():
    """Detailed health check with all component status"""
    try:
        health_data = await health_checker.comprehensive_health_check()
        return health_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Detailed health check failed: {str(e)}")


@router.get("/metrics")
async def get_metrics():
    """Get Prometheus format metrics"""
    try:
        # Update metrics before returning
        await metrics_collector.update_all_metrics()
        
        metrics_content = metrics_collector.generate_prometheus_metrics()
        return Response(
            content=metrics_content,
            media_type=metrics_collector.get_metrics_content_type()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Metrics generation failed: {str(e)}")


@router.get("/metrics/summary")
async def get_metrics_summary():
    """Get metrics summary in JSON format"""
    try:
        # Update metrics before returning
        await metrics_collector.update_all_metrics()
        
        summary = metrics_collector.get_metrics_summary()
        return summary
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Metrics summary failed: {str(e)}")


@router.get("/dashboard")
async def get_dashboard_data():
    """Get dashboard data in JSON format"""
    try:
        dashboard_data = await monitoring_dashboard.get_dashboard_data()
        return dashboard_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Dashboard data failed: {str(e)}")


@router.get("/dashboard/html", response_class=HTMLResponse)
async def get_dashboard_html():
    """Get monitoring dashboard as HTML page"""
    try:
        # Get dashboard data first
        await monitoring_dashboard.get_dashboard_data()
        
        # Generate HTML
        html_content = monitoring_dashboard.generate_html_dashboard()
        return HTMLResponse(content=html_content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Dashboard HTML generation failed: {str(e)}")


@router.get("/alerts")
async def get_alerts(
    alert_type: str = None,
    severity: str = None,
    active_only: bool = True,
    current_user: User = Depends(get_current_user)
):
    """Get alerts with optional filtering"""
    try:
        # Check if user has admin access
        if current_user.role not in ["admin", "administrator"]:
            raise HTTPException(status_code=403, detail="Access denied. Admin role required.")
        
        alerts = []
        
        if active_only:
            alerts = alert_manager.get_active_alerts()
        else:
            alerts = alert_manager.alerts
        
        # Filter by type if specified
        if alert_type:
            try:
                alert_type_enum = AlertType(alert_type)
                alerts = [alert for alert in alerts if alert.type == alert_type_enum]
            except ValueError:
                raise HTTPException(status_code=400, detail=f"Invalid alert type: {alert_type}")
        
        # Filter by severity if specified
        if severity:
            try:
                severity_enum = AlertSeverity(severity)
                alerts = [alert for alert in alerts if alert.severity == severity_enum]
            except ValueError:
                raise HTTPException(status_code=400, detail=f"Invalid severity: {severity}")
        
        # Convert to dict format
        alert_list = []
        for alert in alerts:
            alert_dict = {
                "id": alert.id,
                "type": alert.type.value,
                "severity": alert.severity.value,
                "title": alert.title,
                "message": alert.message,
                "timestamp": alert.timestamp.isoformat(),
                "resolved": alert.resolved,
                "resolved_at": alert.resolved_at.isoformat() if alert.resolved_at else None,
                "acknowledged": alert.acknowledged,
                "acknowledged_at": alert.acknowledged_at.isoformat() if alert.acknowledged_at else None,
                "acknowledged_by": alert.acknowledged_by,
                "metadata": alert.metadata
            }
            alert_list.append(alert_dict)
        
        return {
            "alerts": alert_list,
            "total_count": len(alert_list),
            "filters": {
                "alert_type": alert_type,
                "severity": severity,
                "active_only": active_only
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get alerts: {str(e)}")


@router.get("/alerts/summary")
async def get_alerts_summary(current_user: User = Depends(get_current_user)):
    """Get alert summary statistics"""
    try:
        # Check if user has admin access
        if current_user.role not in ["admin", "administrator"]:
            raise HTTPException(status_code=403, detail="Access denied. Admin role required.")
        
        summary = alert_manager.get_alert_summary()
        return summary
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get alert summary: {str(e)}")


@router.post("/alerts/{alert_id}/acknowledge")
async def acknowledge_alert(
    alert_id: str,
    current_user: User = Depends(get_current_user)
):
    """Acknowledge an alert"""
    try:
        # Check if user has admin access
        if current_user.role not in ["admin", "administrator"]:
            raise HTTPException(status_code=403, detail="Access denied. Admin role required.")
        
        alert = alert_manager.acknowledge_alert(alert_id, current_user.username)
        if not alert:
            raise HTTPException(status_code=404, detail="Alert not found")
        
        return {
            "message": "Alert acknowledged successfully",
            "alert_id": alert_id,
            "acknowledged_by": current_user.username,
            "acknowledged_at": alert.acknowledged_at.isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to acknowledge alert: {str(e)}")


@router.post("/alerts/{alert_id}/resolve")
async def resolve_alert(
    alert_id: str,
    current_user: User = Depends(get_current_user)
):
    """Resolve an alert"""
    try:
        # Check if user has admin access
        if current_user.role not in ["admin", "administrator"]:
            raise HTTPException(status_code=403, detail="Access denied. Admin role required.")
        
        alert = alert_manager.resolve_alert(alert_id, current_user.username)
        if not alert:
            raise HTTPException(status_code=404, detail="Alert not found")
        
        return {
            "message": "Alert resolved successfully",
            "alert_id": alert_id,
            "resolved_by": current_user.username,
            "resolved_at": alert.resolved_at.isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to resolve alert: {str(e)}")


@router.get("/status")
async def get_system_status():
    """Get comprehensive system status"""
    try:
        # Get health data
        health_data = await health_checker.comprehensive_health_check()
        
        # Get metrics summary
        await metrics_collector.update_all_metrics()
        metrics_summary = metrics_collector.get_metrics_summary()
        
        # Get alert summary
        alert_summary = alert_manager.get_alert_summary()
        
        return {
            "timestamp": health_data.get("timestamp"),
            "system": {
                "status": health_data.get("status", "unknown"),
                "response_time_ms": health_data.get("response_time_ms", 0),
                "unhealthy_components": health_data.get("unhealthy_components", [])
            },
            "performance": {
                "uptime_seconds": metrics_summary.get("uptime_seconds", 0),
                "requests": metrics_summary.get("requests", {}),
                "system": metrics_summary.get("system", {})
            },
            "alerts": {
                "active_alerts": alert_summary.get("active_alerts", 0),
                "total_alerts": alert_summary.get("total_alerts", 0),
                "severity_distribution": alert_summary.get("severity_distribution", {})
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"System status check failed: {str(e)}")


@router.get("/components")
async def get_component_status():
    """Get detailed status of all system components"""
    try:
        health_data = await health_checker.comprehensive_health_check()
        components = health_data.get("components", {})
        
        return {
            "timestamp": health_data.get("timestamp"),
            "overall_status": health_data.get("status", "unknown"),
            "components": components
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Component status check failed: {str(e)}")


@router.get("/performance")
async def get_performance_metrics():
    """Get detailed performance metrics"""
    try:
        await metrics_collector.update_all_metrics()
        metrics_summary = metrics_collector.get_metrics_summary()
        
        return {
            "timestamp": metrics_summary.get("timestamp"),
            "performance": {
                "requests": metrics_summary.get("requests", {}),
                "system": metrics_summary.get("system", {}),
                "business": metrics_summary.get("business", {})
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Performance metrics failed: {str(e)}")


@router.get("/business")
async def get_business_metrics():
    """Get business-specific metrics"""
    try:
        await metrics_collector.update_all_metrics()
        metrics_summary = metrics_collector.get_metrics_summary()
        
        return {
            "timestamp": metrics_summary.get("timestamp"),
            "business_metrics": metrics_summary.get("business", {})
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Business metrics failed: {str(e)}") 
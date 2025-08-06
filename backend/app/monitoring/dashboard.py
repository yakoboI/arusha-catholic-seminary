"""
Monitoring Dashboard Module

Provides a comprehensive monitoring dashboard with real-time metrics,
health status, and system information visualization.
"""

import json
import structlog
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from fastapi import HTTPException
from fastapi.responses import HTMLResponse
from app.config import settings
from .health import health_checker
from .metrics import metrics_collector
from .alerts import alert_manager, AlertType, AlertSeverity

logger = structlog.get_logger(__name__)


class MonitoringDashboard:
    """Comprehensive monitoring dashboard"""
    
    def __init__(self):
        self.last_update = None
        self.dashboard_data = {}
        
    async def get_dashboard_data(self) -> Dict[str, Any]:
        """Get comprehensive dashboard data"""
        try:
            # Get health status
            health_data = await health_checker.comprehensive_health_check()
            
            # Get metrics summary
            metrics_data = metrics_collector.get_metrics_summary()
            
            # Get alert summary
            alert_summary = alert_manager.get_alert_summary()
            
            # Get active alerts
            active_alerts = alert_manager.get_active_alerts()
            
            # Check for new alerts based on current data
            await self._check_and_create_alerts(health_data, metrics_data)
            
            # Compile dashboard data
            dashboard_data = {
                "timestamp": datetime.utcnow().isoformat(),
                "system": {
                    "name": settings.APP_NAME,
                    "version": settings.APP_VERSION,
                    "environment": "development" if settings.DEBUG else "production",
                    "uptime_seconds": metrics_data.get("uptime_seconds", 0),
                    "status": health_data.get("status", "unknown")
                },
                "health": {
                    "overall_status": health_data.get("status", "unknown"),
                    "response_time_ms": health_data.get("response_time_ms", 0),
                    "unhealthy_components": health_data.get("unhealthy_components", []),
                    "components": health_data.get("components", {})
                },
                "performance": {
                    "requests": metrics_data.get("requests", {}),
                    "system": metrics_data.get("system", {}),
                    "business": metrics_data.get("business", {})
                },
                "alerts": {
                    "summary": alert_summary,
                    "active_alerts": [
                        {
                            "id": alert.id,
                            "type": alert.type.value,
                            "severity": alert.severity.value,
                            "title": alert.title,
                            "message": alert.message,
                            "timestamp": alert.timestamp.isoformat(),
                            "acknowledged": alert.acknowledged,
                            "acknowledged_by": alert.acknowledged_by
                        }
                        for alert in active_alerts[:10]  # Show last 10 alerts
                    ]
                },
                "quick_stats": self._generate_quick_stats(health_data, metrics_data, alert_summary)
            }
            
            self.dashboard_data = dashboard_data
            self.last_update = datetime.utcnow()
            
            return dashboard_data
            
        except Exception as e:
            logger.error("Failed to generate dashboard data", error=str(e))
            raise HTTPException(status_code=500, detail=f"Dashboard data generation failed: {str(e)}")
    
    def _generate_quick_stats(self, health_data: Dict, metrics_data: Dict, alert_summary: Dict) -> Dict[str, Any]:
        """Generate quick statistics for dashboard"""
        return {
            "system_health": health_data.get("status", "unknown"),
            "response_time_ms": health_data.get("response_time_ms", 0),
            "error_rate_percent": metrics_data.get("requests", {}).get("error_rate_percent", 0),
            "cpu_usage_percent": metrics_data.get("system", {}).get("cpu_usage_percent", 0),
            "memory_usage_percent": metrics_data.get("system", {}).get("memory_usage_percent", 0),
            "disk_usage_percent": metrics_data.get("system", {}).get("disk_usage_percent", 0),
            "active_alerts": alert_summary.get("active_alerts", 0),
            "total_users": metrics_data.get("business", {}).get("users_total", 0),
            "total_students": metrics_data.get("business", {}).get("students_total", 0),
            "total_teachers": metrics_data.get("business", {}).get("teachers_total", 0)
        }
    
    async def _check_and_create_alerts(self, health_data: Dict, metrics_data: Dict):
        """Check current data and create alerts if needed"""
        try:
            # Check health alerts
            alert_manager.check_health_alerts(health_data)
            
            # Check performance alerts
            alert_manager.check_performance_alerts(metrics_data)
            
            # Check resource alerts
            system_data = health_data.get("components", {}).get("system", {})
            alert_manager.check_resource_alerts(system_data)
            
            # Check business alerts
            business_data = health_data.get("components", {}).get("application", {})
            alert_manager.check_business_alerts(business_data)
            
        except Exception as e:
            logger.error("Failed to check and create alerts", error=str(e))
    
    def get_health_status_color(self, status: str) -> str:
        """Get color for health status"""
        status_colors = {
            "healthy": "green",
            "unhealthy": "red",
            "warning": "yellow",
            "unknown": "gray"
        }
        return status_colors.get(status, "gray")
    
    def get_severity_color(self, severity: str) -> str:
        """Get color for alert severity"""
        severity_colors = {
            "info": "blue",
            "warning": "yellow",
            "error": "red",
            "critical": "purple"
        }
        return severity_colors.get(severity, "gray")
    
    def generate_html_dashboard(self) -> str:
        """Generate HTML dashboard"""
        try:
            dashboard_data = self.dashboard_data
            if not dashboard_data:
                return self._generate_empty_dashboard()
            
            # Extract data for template
            system = dashboard_data.get("system", {})
            health = dashboard_data.get("health", {})
            performance = dashboard_data.get("performance", {})
            alerts = dashboard_data.get("alerts", {})
            quick_stats = dashboard_data.get("quick_stats", {})
            
            # Generate HTML
            html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{system.get('name', 'Monitoring Dashboard')}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
        }}
        
        .header {{
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            border-radius: 15px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        }}
        
        .header h1 {{
            color: #2d3748;
            font-size: 2.5rem;
            margin-bottom: 10px;
            text-align: center;
        }}
        
        .header .subtitle {{
            color: #718096;
            text-align: center;
            font-size: 1.1rem;
        }}
        
        .status-badge {{
            display: inline-block;
            padding: 8px 16px;
            border-radius: 20px;
            font-weight: bold;
            font-size: 0.9rem;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        
        .status-healthy {{ background: #c6f6d5; color: #22543d; }}
        .status-unhealthy {{ background: #fed7d7; color: #742a2a; }}
        .status-warning {{ background: #fef5e7; color: #744210; }}
        
        .grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }}
        
        .card {{
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            border-radius: 15px;
            padding: 20px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
            transition: transform 0.3s ease;
        }}
        
        .card:hover {{
            transform: translateY(-5px);
        }}
        
        .card h3 {{
            color: #2d3748;
            margin-bottom: 15px;
            font-size: 1.3rem;
            border-bottom: 2px solid #e2e8f0;
            padding-bottom: 10px;
        }}
        
        .metric {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 10px 0;
            border-bottom: 1px solid #f7fafc;
        }}
        
        .metric:last-child {{
            border-bottom: none;
        }}
        
        .metric-label {{
            color: #4a5568;
            font-weight: 500;
        }}
        
        .metric-value {{
            color: #2d3748;
            font-weight: bold;
            font-size: 1.1rem;
        }}
        
        .alert-item {{
            background: #f7fafc;
            border-radius: 8px;
            padding: 15px;
            margin-bottom: 10px;
            border-left: 4px solid #e2e8f0;
        }}
        
        .alert-error {{ border-left-color: #f56565; }}
        .alert-warning {{ border-left-color: #ed8936; }}
        .alert-info {{ border-left-color: #4299e1; }}
        
        .alert-title {{
            font-weight: bold;
            color: #2d3748;
            margin-bottom: 5px;
        }}
        
        .alert-message {{
            color: #4a5568;
            font-size: 0.9rem;
        }}
        
        .alert-meta {{
            color: #718096;
            font-size: 0.8rem;
            margin-top: 5px;
        }}
        
        .progress-bar {{
            width: 100%;
            height: 8px;
            background: #e2e8f0;
            border-radius: 4px;
            overflow: hidden;
            margin-top: 5px;
        }}
        
        .progress-fill {{
            height: 100%;
            background: linear-gradient(90deg, #48bb78, #38a169);
            transition: width 0.3s ease;
        }}
        
        .progress-fill.warning {{ background: linear-gradient(90deg, #ed8936, #dd6b20); }}
        .progress-fill.danger {{ background: linear-gradient(90deg, #f56565, #e53e3e); }}
        
        .refresh-info {{
            text-align: center;
            color: #718096;
            font-size: 0.9rem;
            margin-top: 20px;
        }}
        
        @media (max-width: 768px) {{
            .grid {{
                grid-template-columns: 1fr;
            }}
            
            .header h1 {{
                font-size: 2rem;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 {system.get('name', 'Monitoring Dashboard')}</h1>
            <div class="subtitle">
                System Status: 
                <span class="status-badge status-{health.get('overall_status', 'unknown')}">
                    {health.get('overall_status', 'Unknown').upper()}
                </span>
                | Version: {system.get('version', 'Unknown')} | 
                Environment: {system.get('environment', 'Unknown').title()}
            </div>
        </div>
        
        <div class="grid">
            <!-- System Health -->
            <div class="card">
                <h3>🏥 System Health</h3>
                <div class="metric">
                    <span class="metric-label">Overall Status</span>
                    <span class="metric-value status-badge status-{health.get('overall_status', 'unknown')}">
                        {health.get('overall_status', 'Unknown').upper()}
                    </span>
                </div>
                <div class="metric">
                    <span class="metric-label">Response Time</span>
                    <span class="metric-value">{health.get('response_time_ms', 0)}ms</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Unhealthy Components</span>
                    <span class="metric-value">{len(health.get('unhealthy_components', []))}</span>
                </div>
            </div>
            
            <!-- Performance Metrics -->
            <div class="card">
                <h3>⚡ Performance</h3>
                <div class="metric">
                    <span class="metric-label">Total Requests</span>
                    <span class="metric-value">{performance.get('requests', {}).get('total', 0)}</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Error Rate</span>
                    <span class="metric-value">{performance.get('requests', {}).get('error_rate_percent', 0)}%</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Avg Response Time</span>
                    <span class="metric-value">{performance.get('requests', {}).get('avg_response_time_ms', 0)}ms</span>
                </div>
            </div>
            
            <!-- System Resources -->
            <div class="card">
                <h3>💻 System Resources</h3>
                <div class="metric">
                    <span class="metric-label">CPU Usage</span>
                    <span class="metric-value">{performance.get('system', {}).get('cpu_usage_percent', 0)}%</span>
                </div>
                <div class="progress-bar">
                    <div class="progress-fill {'warning' if performance.get('system', {}).get('cpu_usage_percent', 0) > 70 else 'danger' if performance.get('system', {}).get('cpu_usage_percent', 0) > 90 else ''}" 
                         style="width: {performance.get('system', {}).get('cpu_usage_percent', 0)}%"></div>
                </div>
                
                <div class="metric">
                    <span class="metric-label">Memory Usage</span>
                    <span class="metric-value">{performance.get('system', {}).get('memory_usage_percent', 0)}%</span>
                </div>
                <div class="progress-bar">
                    <div class="progress-fill {'warning' if performance.get('system', {}).get('memory_usage_percent', 0) > 70 else 'danger' if performance.get('system', {}).get('memory_usage_percent', 0) > 90 else ''}" 
                         style="width: {performance.get('system', {}).get('memory_usage_percent', 0)}%"></div>
                </div>
                
                <div class="metric">
                    <span class="metric-label">Disk Usage</span>
                    <span class="metric-value">{performance.get('system', {}).get('disk_usage_percent', 0)}%</span>
                </div>
                <div class="progress-bar">
                    <div class="progress-fill {'warning' if performance.get('system', {}).get('disk_usage_percent', 0) > 70 else 'danger' if performance.get('system', {}).get('disk_usage_percent', 0) > 90 else ''}" 
                         style="width: {performance.get('system', {}).get('disk_usage_percent', 0)}%"></div>
                </div>
            </div>
            
            <!-- Business Metrics -->
            <div class="card">
                <h3>📊 Business Metrics</h3>
                <div class="metric">
                    <span class="metric-label">Total Users</span>
                    <span class="metric-value">{performance.get('business', {}).get('users_total', 0)}</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Total Students</span>
                    <span class="metric-value">{performance.get('business', {}).get('students_total', 0)}</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Total Teachers</span>
                    <span class="metric-value">{performance.get('business', {}).get('teachers_total', 0)}</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Total Classes</span>
                    <span class="metric-value">{performance.get('business', {}).get('classes_total', 0)}</span>
                </div>
            </div>
            
            <!-- Alerts -->
            <div class="card">
                <h3>🚨 Active Alerts ({alerts.get('summary', {}).get('active_alerts', 0)})</h3>
                {self._generate_alerts_html(alerts.get('active_alerts', []))}
            </div>
            
            <!-- System Info -->
            <div class="card">
                <h3>ℹ️ System Information</h3>
                <div class="metric">
                    <span class="metric-label">Uptime</span>
                    <span class="metric-value">{self._format_uptime(system.get('uptime_seconds', 0))}</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Last Update</span>
                    <span class="metric-value">{dashboard_data.get('timestamp', 'Unknown')}</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Total Alerts</span>
                    <span class="metric-value">{alerts.get('summary', {}).get('total_alerts', 0)}</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Resolved Alerts</span>
                    <span class="metric-value">{alerts.get('summary', {}).get('resolved_alerts', 0)}</span>
                </div>
            </div>
        </div>
        
        <div class="refresh-info">
            💡 Dashboard auto-refreshes every 30 seconds | Last updated: {dashboard_data.get('timestamp', 'Unknown')}
        </div>
    </div>
    
    <script>
        // Auto-refresh dashboard every 30 seconds
        setTimeout(() => {{
            window.location.reload();
        }}, 30000);
    </script>
</body>
</html>
            """
            
            return html
            
        except Exception as e:
            logger.error("Failed to generate HTML dashboard", error=str(e))
            return self._generate_error_dashboard(str(e))
    
    def _generate_alerts_html(self, alerts: List[Dict]) -> str:
        """Generate HTML for alerts section"""
        if not alerts:
            return '<div class="alert-item"><div class="alert-message">No active alerts</div></div>'
        
        html = ""
        for alert in alerts:
            severity_class = f"alert-{alert.get('severity', 'info')}"
            html += f"""
            <div class="alert-item {severity_class}">
                <div class="alert-title">{alert.get('title', 'Unknown Alert')}</div>
                <div class="alert-message">{alert.get('message', 'No message')}</div>
                <div class="alert-meta">
                    {alert.get('timestamp', 'Unknown time')} | 
                    Type: {alert.get('type', 'Unknown')} | 
                    Severity: {alert.get('severity', 'Unknown')}
                </div>
            </div>
            """
        return html
    
    def _format_uptime(self, seconds: float) -> str:
        """Format uptime in human readable format"""
        if seconds < 60:
            return f"{int(seconds)}s"
        elif seconds < 3600:
            return f"{int(seconds // 60)}m {int(seconds % 60)}s"
        elif seconds < 86400:
            hours = int(seconds // 3600)
            minutes = int((seconds % 3600) // 60)
            return f"{hours}h {minutes}m"
        else:
            days = int(seconds // 86400)
            hours = int((seconds % 86400) // 3600)
            return f"{days}d {hours}h"
    
    def _generate_empty_dashboard(self) -> str:
        """Generate empty dashboard when no data is available"""
        return """
<!DOCTYPE html>
<html>
<head>
    <title>Monitoring Dashboard</title>
    <style>
        body { font-family: Arial, sans-serif; text-align: center; padding: 50px; }
        .error { color: #e53e3e; }
    </style>
</head>
<body>
    <h1>Monitoring Dashboard</h1>
    <p class="error">No dashboard data available</p>
    <p>Please refresh the page or check the monitoring service.</p>
</body>
</html>
        """
    
    def _generate_error_dashboard(self, error: str) -> str:
        """Generate error dashboard"""
        return f"""
<!DOCTYPE html>
<html>
<head>
    <title>Monitoring Dashboard - Error</title>
    <style>
        body {{ font-family: Arial, sans-serif; text-align: center; padding: 50px; }}
        .error {{ color: #e53e3e; }}
    </style>
</head>
<body>
    <h1>Monitoring Dashboard</h1>
    <p class="error">Error generating dashboard</p>
    <p>{error}</p>
</body>
</html>
        """


# Global dashboard instance
monitoring_dashboard = MonitoringDashboard() 
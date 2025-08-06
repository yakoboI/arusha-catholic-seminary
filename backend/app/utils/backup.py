import os
import shutil
import sqlite3
import zipfile
from datetime import datetime, timedelta
from pathlib import Path
import structlog
from app.config import settings

logger = structlog.get_logger()

class DatabaseBackup:
    """Database backup utility for SQLite databases"""
    
    def __init__(self):
        self.backup_dir = Path(settings.BACKUP_DIR)
        self.backup_dir.mkdir(exist_ok=True)
        self.db_path = Path("arusha_seminary.db")
    
    def create_backup(self, include_uploads: bool = True) -> str:
        """Create a backup of the database and optionally uploads"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"backup_{timestamp}"
        backup_path = self.backup_dir / backup_name
        
        try:
            # Create backup directory
            backup_path.mkdir(exist_ok=True)
            
            # Backup database
            if self.db_path.exists():
                backup_db_path = backup_path / "arusha_seminary.db"
                shutil.copy2(self.db_path, backup_db_path)
                logger.info("Database backup created", backup_path=str(backup_db_path))
            
            # Backup uploads directory
            if include_uploads and Path("uploads").exists():
                backup_uploads_path = backup_path / "uploads"
                shutil.copytree("uploads", backup_uploads_path)
                logger.info("Uploads backup created", backup_path=str(backup_uploads_path))
            
            # Create zip archive
            zip_path = self.backup_dir / f"{backup_name}.zip"
            self._create_zip_archive(backup_path, zip_path)
            
            # Clean up temporary directory
            shutil.rmtree(backup_path)
            
            logger.info("Backup completed successfully", zip_path=str(zip_path))
            return str(zip_path)
            
        except Exception as e:
            logger.error("Backup failed", error=str(e))
            raise
    
    def _create_zip_archive(self, source_path: Path, zip_path: Path):
        """Create a zip archive of the backup"""
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file_path in source_path.rglob('*'):
                if file_path.is_file():
                    arcname = file_path.relative_to(source_path)
                    zipf.write(file_path, arcname)
    
    def restore_backup(self, backup_path: str) -> bool:
        """Restore database from backup"""
        try:
            backup_path = Path(backup_path)
            if not backup_path.exists():
                raise FileNotFoundError(f"Backup file not found: {backup_path}")
            
            # Extract backup
            temp_dir = self.backup_dir / "temp_restore"
            temp_dir.mkdir(exist_ok=True)
            
            with zipfile.ZipFile(backup_path, 'r') as zipf:
                zipf.extractall(temp_dir)
            
            # Restore database
            backup_db = temp_dir / "arusha_seminary.db"
            if backup_db.exists():
                # Create backup of current database
                if self.db_path.exists():
                    current_backup = self.backup_dir / f"pre_restore_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
                    shutil.copy2(self.db_path, current_backup)
                
                # Restore database
                shutil.copy2(backup_db, self.db_path)
                logger.info("Database restored successfully")
            
            # Restore uploads
            backup_uploads = temp_dir / "uploads"
            if backup_uploads.exists():
                if Path("uploads").exists():
                    shutil.rmtree("uploads")
                shutil.copytree(backup_uploads, "uploads")
                logger.info("Uploads restored successfully")
            
            # Clean up
            shutil.rmtree(temp_dir)
            return True
            
        except Exception as e:
            logger.error("Restore failed", error=str(e))
            return False
    
    def cleanup_old_backups(self, days_to_keep: int = None) -> int:
        """Clean up old backup files"""
        if days_to_keep is None:
            days_to_keep = settings.BACKUP_RETENTION_DAYS
        
        cutoff_date = datetime.now() - timedelta(days=days_to_keep)
        deleted_count = 0
        
        for backup_file in self.backup_dir.glob("*.zip"):
            try:
                file_time = datetime.fromtimestamp(backup_file.stat().st_mtime)
                if file_time < cutoff_date:
                    backup_file.unlink()
                    deleted_count += 1
                    logger.info("Deleted old backup", file=str(backup_file))
            except Exception as e:
                logger.error("Failed to delete backup", file=str(backup_file), error=str(e))
        
        logger.info("Backup cleanup completed", deleted_count=deleted_count)
        return deleted_count
    
    def list_backups(self) -> list:
        """List all available backups"""
        backups = []
        for backup_file in self.backup_dir.glob("*.zip"):
            try:
                stat = backup_file.stat()
                backups.append({
                    "filename": backup_file.name,
                    "size": stat.st_size,
                    "created": datetime.fromtimestamp(stat.st_mtime),
                    "path": str(backup_file)
                })
            except Exception as e:
                logger.error("Failed to read backup info", file=str(backup_file), error=str(e))
        
        # Sort by creation date (newest first)
        backups.sort(key=lambda x: x["created"], reverse=True)
        return backups
    
    def get_backup_size(self) -> int:
        """Get total size of all backups"""
        total_size = 0
        for backup_file in self.backup_dir.glob("*.zip"):
            total_size += backup_file.stat().st_size
        return total_size


class DatabaseMaintenance:
    """Database maintenance utilities"""
    
    def __init__(self):
        self.db_path = "arusha_seminary.db"
    
    def optimize_database(self) -> bool:
        """Optimize SQLite database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Run VACUUM to optimize database
            cursor.execute("VACUUM")
            
            # Analyze tables for better query planning
            cursor.execute("ANALYZE")
            
            # Update statistics
            cursor.execute("PRAGMA optimize")
            
            conn.commit()
            conn.close()
            
            logger.info("Database optimization completed")
            return True
            
        except Exception as e:
            logger.error("Database optimization failed", error=str(e))
            return False
    
    def check_database_integrity(self) -> dict:
        """Check database integrity"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Check integrity
            cursor.execute("PRAGMA integrity_check")
            integrity_result = cursor.fetchone()
            
            # Get database info
            cursor.execute("PRAGMA page_count")
            page_count = cursor.fetchone()[0]
            
            cursor.execute("PRAGMA page_size")
            page_size = cursor.fetchone()[0]
            
            cursor.execute("PRAGMA freelist_count")
            freelist_count = cursor.fetchone()[0]
            
            conn.close()
            
            result = {
                "integrity": integrity_result[0] == "ok",
                "size_mb": (page_count * page_size) / (1024 * 1024),
                "freelist_count": freelist_count,
                "last_check": datetime.now()
            }
            
            logger.info("Database integrity check completed", result=result)
            return result
            
        except Exception as e:
            logger.error("Database integrity check failed", error=str(e))
            return {"integrity": False, "error": str(e)}


# Utility functions
def create_scheduled_backup():
    """Create a scheduled backup (can be called by cron job)"""
    backup = DatabaseBackup()
    try:
        backup_path = backup.create_backup()
        backup.cleanup_old_backups()
        return backup_path
    except Exception as e:
        logger.error("Scheduled backup failed", error=str(e))
        return None


def get_backup_status() -> dict:
    """Get backup system status"""
    backup = DatabaseBackup()
    maintenance = DatabaseMaintenance()
    
    return {
        "backups": backup.list_backups(),
        "total_size_mb": backup.get_backup_size() / (1024 * 1024),
        "database_integrity": maintenance.check_database_integrity(),
        "backup_directory": str(backup.backup_dir),
        "retention_days": settings.BACKUP_RETENTION_DAYS
    } 
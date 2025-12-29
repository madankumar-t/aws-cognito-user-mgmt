"""Audit logging service."""

from typing import Dict, Optional
from datetime import datetime
from src.utils.logger import get_logger

logger = get_logger(__name__)


class AuditService:
    """Service for audit logging."""
    
    async def log_operation(
        self,
        user_id: str,
        operation: str,
        resource_type: str,
        resource_id: str,
        account_id: Optional[str] = None,
        region: Optional[str] = None,
        details: Optional[Dict] = None
    ):
        """Log an audit event."""
        audit_log = {
            "timestamp": datetime.utcnow().isoformat(),
            "user_id": user_id,
            "operation": operation,
            "resource_type": resource_type,
            "resource_id": resource_id,
            "account_id": account_id,
            "region": region,
            "details": details or {}
        }
        
        logger.info("audit_event", extra=audit_log)


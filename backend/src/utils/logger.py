"""Structured logging configuration."""

import logging
import json
import os
from datetime import datetime
from typing import Any, Dict


class CloudWatchJSONFormatter(logging.Formatter):
    """JSON formatter for CloudWatch Logs."""
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON."""
        log_data: Dict[str, Any] = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }
        
        # Add extra context if present
        if hasattr(record, "extra"):
            log_data.update(record.extra)
        
        # Add Lambda context if available
        if hasattr(record, "aws_request_id"):
            log_data["aws_request_id"] = record.aws_request_id
        
        return json.dumps(log_data)


def get_logger(name: str) -> logging.Logger:
    """Get configured logger with JSON formatting."""
    logger = logging.getLogger(name)
    logger.setLevel(os.getenv("LOG_LEVEL", "INFO"))
    
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(CloudWatchJSONFormatter())
        logger.addHandler(handler)
    
    return logger


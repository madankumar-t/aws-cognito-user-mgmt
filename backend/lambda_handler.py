"""AWS Lambda handler for API Gateway HTTP API."""

import json
import os
import sys
from mangum import Mangum

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from src.main import app
from src.utils.logger import get_logger

logger = get_logger(__name__)

# Initialize Mangum adapter
handler = Mangum(
    app,
    lifespan="off",  # Disable lifespan events in Lambda
    log_level=os.getenv("LOG_LEVEL", "INFO")
)


def lambda_handler(event, context):
    """
    AWS Lambda handler for API Gateway HTTP API.
    
    This handler processes API Gateway events and routes them
    through the FastAPI application.
    """
    try:
        # Log request
        logger.info(
            "lambda_invocation",
            extra={
                "aws_request_id": context.aws_request_id,
                "function_name": context.function_name,
                "path": event.get("rawPath", ""),
                "method": event.get("requestContext", {}).get("http", {}).get("method", "")
            }
        )
        
        # Process request
        response = handler(event, context)
        
        # Log response
        logger.info(
            "lambda_response",
            extra={
                "aws_request_id": context.aws_request_id,
                "status_code": response.get("statusCode", 500)
            }
        )
        
        return response
        
    except Exception as e:
        # Log error
        logger.error(
            "lambda_error",
            extra={
                "aws_request_id": context.aws_request_id,
                "error": str(e),
                "error_type": type(e).__name__
            },
            exc_info=True
        )
        
        # Return error response
        return {
            "statusCode": 500,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": os.getenv("ALLOWED_ORIGINS", "*")
            },
            "body": json.dumps({
                "error": {
                    "code": "INTERNAL_SERVER_ERROR",
                    "message": "An unexpected error occurred",
                    "request_id": context.aws_request_id
                }
            })
        }


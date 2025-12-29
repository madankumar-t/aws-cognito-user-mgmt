# Example AWS Lambda Handler (Python 3.12)
## AWS Cognito User Management Application

**Document Version:** 1.0  
**Date:** 2024

---

## 1. Lambda Handler Entry Point

```python
# lambda_handler.py

import json
import os
from mangum import Mangum
from src.main import app

# Initialize Mangum adapter for FastAPI
handler = Mangum(app, lifespan="off")

def lambda_handler(event, context):
    """
    AWS Lambda handler for API Gateway HTTP API.
    
    Args:
        event: API Gateway event
        context: Lambda context
    
    Returns:
        API Gateway response
    """
    try:
        # Process request through FastAPI
        response = handler(event, context)
        
        return response
        
    except Exception as e:
        # Global error handler
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
                    "details": {}
                }
            })
        }
```

---

## 2. Alternative: Direct Lambda Handler (Without Mangum)

```python
# lambda_handler.py (Alternative implementation)

import json
import os
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from src.main import app

def lambda_handler(event, context):
    """
    Direct Lambda handler without Mangum.
    Converts API Gateway event to ASGI scope.
    """
    from asgiref.wsgi import WsgiToAsgi
    from mangum import Mangum
    
    # Convert FastAPI app to ASGI
    asgi_app = Mangum(app)
    
    # Convert API Gateway event to ASGI scope
    scope = {
        "type": "http",
        "method": event.get("requestContext", {}).get("http", {}).get("method", "GET"),
        "path": event.get("rawPath", "/"),
        "query_string": event.get("rawQueryString", "").encode(),
        "headers": [
            [k.encode(), v.encode()] for k, v in event.get("headers", {}).items()
        ],
        "server": ("localhost", 80),
        "client": ("127.0.0.1", 0),
    }
    
    # Create ASGI message
    async def receive():
        return {
            "type": "http.request",
            "body": event.get("body", "").encode() if event.get("body") else b""
        }
    
    async def send(message):
        pass  # Response handled by Mangum
    
    # Process request
    import asyncio
    response = asyncio.run(asgi_app(scope, receive, send))
    
    return response
```

---

## 3. Lambda Function Configuration

### 3.1 Environment Variables

```yaml
# sam-template.yaml (excerpt)

Resources:
  CognitoManagementFunction:
    Type: AWS::Serverless::Function
    Properties:
      Runtime: python3.12
      Handler: lambda_handler.lambda_handler
      CodeUri: backend/
      Environment:
        Variables:
          ENTRA_ID_TENANT_ID: !Ref EntraIdTenantId
          ENTRA_ID_CLIENT_ID: !Ref EntraIdClientId
          ENTRA_ID_AUDIENCE: !Ref EntraIdAudience
          JWKS_URL: !Sub "https://login.microsoftonline.com/${EntraIdTenantId}/discovery/v2.0/keys"
          ACCOUNT_ROLE_NAME: CognitoManagementRole
          DEFAULT_REGION: us-east-1
          LOG_LEVEL: INFO
          ALLOWED_ORIGINS: !Ref AllowedOrigins
          ADMIN_GROUP_NAME: cognito-admin
          DEVELOPER_GROUP_NAME: cognito-developer
      Timeout: 30
      MemorySize: 512
      Policies:
        - Statement:
            - Effect: Allow
              Action:
                - sts:AssumeRole
              Resource: !Sub "arn:aws:iam::*:role/${AccountRoleName}"
```

---

## 4. Lambda Layer for Dependencies

### 4.1 Creating Lambda Layer

```bash
# build-layer.sh

#!/bin/bash

# Create layer directory
mkdir -p layer/python

# Install dependencies
pip install -r requirements.txt -t layer/python/

# Create zip file
cd layer
zip -r ../lambda-layer.zip python/
cd ..
```

### 4.2 SAM Template with Layer

```yaml
# sam-template.yaml (Layer definition)

Resources:
  DependenciesLayer:
    Type: AWS::Serverless::LayerVersion
    Properties:
      LayerName: cognito-management-dependencies
      ContentUri: layer/
      CompatibleRuntimes:
        - python3.11
      RetentionPolicy: Retain

  CognitoManagementFunction:
    Type: AWS::Serverless::Function
    Properties:
      Layers:
        - !Ref DependenciesLayer
      # ... other properties
```

---

## 5. Cold Start Optimization

### 5.1 Connection Pooling

```python
# services/sts_service.py (Optimized)

import boto3
from functools import lru_cache

class STSService:
    """Optimized STS service with connection reuse."""
    
    @lru_cache(maxsize=1)
    def _get_sts_client(self):
        """Cached STS client (reused across invocations)."""
        return boto3.client("sts")
    
    def __init__(self):
        self.sts_client = self._get_sts_client()
        self.credential_cache = {}
```

### 5.2 Module-Level Initialization

```python
# src/main.py (Optimized)

# Initialize services at module level (reused across invocations)
from src.services.sts_service import STSService
from src.services.audit_service import AuditService

# These are reused across Lambda invocations
sts_service = STSService()
audit_service = AuditService()

app = FastAPI(...)
```

---

## 6. Error Handling in Lambda

### 6.1 Structured Error Responses

```python
# utils/exceptions.py

class CognitoManagementException(Exception):
    """Base exception."""
    def __init__(self, message: str, code: str = "GENERIC_ERROR", status_code: int = 500):
        self.message = message
        self.code = code
        self.status_code = status_code
        super().__init__(self.message)

# In Lambda handler
def lambda_handler(event, context):
    try:
        response = handler(event, context)
        return response
    except CognitoManagementException as e:
        return {
            "statusCode": e.status_code,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*"
            },
            "body": json.dumps({
                "error": {
                    "code": e.code,
                    "message": e.message
                }
            })
        }
```

---

## 7. Logging in Lambda

### 7.1 CloudWatch Logs Integration

```python
# utils/logger.py

import logging
import json
import os
from datetime import datetime

class CloudWatchJSONFormatter(logging.Formatter):
    """JSON formatter for CloudWatch Logs."""
    
    def format(self, record):
        log_data = {
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
    """Get configured logger."""
    logger = logging.getLogger(name)
    logger.setLevel(os.getenv("LOG_LEVEL", "INFO"))
    
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(CloudWatchJSONFormatter())
        logger.addHandler(handler)
    
    return logger
```

---

## 8. Testing Lambda Locally

### 8.1 Local Testing Script

```python
# tests/local_lambda_test.py

import json
from lambda_handler import lambda_handler

# Sample API Gateway event
event = {
    "version": "2.0",
    "routeKey": "GET /api/v1/health",
    "rawPath": "/api/v1/health",
    "rawQueryString": "",
    "headers": {
        "content-type": "application/json"
    },
    "requestContext": {
        "http": {
            "method": "GET",
            "path": "/api/v1/health"
        }
    },
    "body": None
}

context = {
    "request_id": "test-request-id",
    "function_name": "CognitoManagementFunction"
}

# Test handler
response = lambda_handler(event, context)
print(json.dumps(response, indent=2))
```

### 8.2 SAM Local Testing

```bash
# Test locally with SAM CLI
sam local start-api

# Test specific endpoint
sam local invoke CognitoManagementFunction -e events/test-event.json
```

---

## 9. Lambda Performance Tuning

### 9.1 Memory Configuration

```yaml
# sam-template.yaml

CognitoManagementFunction:
  Properties:
    MemorySize: 512  # Adjust based on profiling
    Timeout: 30      # Maximum timeout
```

### 9.2 Provisioned Concurrency (Optional)

```yaml
# For low-latency requirements

CognitoManagementFunction:
  Properties:
    ProvisionedConcurrencyConfig:
      ProvisionedConcurrentExecutions: 5
```

---

## 10. Monitoring and Metrics

### 10.1 Custom Metrics

```python
# utils/metrics.py

import boto3

cloudwatch = boto3.client("cloudwatch")

def put_metric(metric_name: str, value: float, unit: str = "Count"):
    """Put custom CloudWatch metric."""
    cloudwatch.put_metric_data(
        Namespace="CognitoManagement",
        MetricData=[
            {
                "MetricName": metric_name,
                "Value": value,
                "Unit": unit
            }
        ]
    )

# Usage in code
put_metric("UsersCreated", 1)
put_metric("APIResponseTime", 1.5, "Seconds")
```

---

## 11. Complete Lambda Handler Example

```python
# lambda_handler.py (Complete)

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
```

---

**Document Control**

- **Version**: 1.0
- **Last Updated**: 2024


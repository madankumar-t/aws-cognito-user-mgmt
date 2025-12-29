"""FastAPI application entry point."""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from src.middleware.auth import JWTAuthMiddleware
from src.middleware.logging import LoggingMiddleware
from src.middleware.error_handler import error_handler
from src.routes import auth, accounts, pools, users
from src.config import settings
from src.utils.logger import get_logger
from src.utils.exceptions import CognitoManagementException

logger = get_logger(__name__)

app = FastAPI(
    title="AWS Cognito User Management API",
    description="Enterprise-grade Cognito user management with Microsoft Entra ID authentication",
    version="1.0.0"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Custom Middleware
app.middleware("http")(LoggingMiddleware())
app.middleware("http")(JWTAuthMiddleware())

# Global Exception Handler
app.exception_handler(CognitoManagementException)(error_handler)

# Include Routers
app.include_router(auth.router, prefix="/api/v1", tags=["Authentication"])
app.include_router(accounts.router, prefix="/api/v1", tags=["Accounts"])
app.include_router(pools.router, prefix="/api/v1", tags=["Pools"])
app.include_router(users.router, prefix="/api/v1", tags=["Users"])


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "version": "1.0.0"}


@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "AWS Cognito User Management API"}


# Generic exception handler
@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    """Handle all unhandled exceptions."""
    logger.error(
        "unhandled_exception",
        extra={
            "error": str(exc),
            "error_type": type(exc).__name__,
            "path": request.url.path,
            "method": request.method
        },
        exc_info=True
    )
    
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected error occurred"
            }
        }
    )


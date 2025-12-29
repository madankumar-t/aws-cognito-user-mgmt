"""Pytest configuration and fixtures."""

import pytest
from unittest.mock import Mock, patch
from fastapi.testclient import TestClient
from src.main import app


@pytest.fixture
def client():
    """Test client for FastAPI app."""
    return TestClient(app)


@pytest.fixture
def mock_jwt_token():
    """Mock JWT token."""
    return "mock.jwt.token"


@pytest.fixture
def mock_user_claims():
    """Mock user claims from JWT."""
    return {
        "sub": "user-123",
        "email": "user@example.com",
        "name": "Test User",
        "groups": ["cognito-admin"]
    }


@pytest.fixture
def mock_sts_credentials():
    """Mock STS credentials."""
    return {
        "AccessKeyId": "AKIAIOSFODNN7EXAMPLE",
        "SecretAccessKey": "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY",
        "SessionToken": "mock-session-token"
    }


"""Configuration management for the application."""

from pydantic_settings import BaseSettings
from typing import List, Optional
import os


class Settings(BaseSettings):
    """Application settings."""
    
    # Microsoft Entra ID Configuration
    entra_id_tenant_id: str
    entra_id_client_id: str
    entra_id_audience: str
    jwks_url: Optional[str] = None  # Auto-constructed if not provided
    
    # AWS Configuration
    account_role_name: str = "CognitoManagementRole"
    default_region: str = "us-east-1"
    
    # Application Configuration
    log_level: str = "INFO"
    allowed_origins: List[str] = ["http://localhost:3000"]
    
    # Role Mapping
    admin_group_name: str = "cognito-admin"
    developer_group_name: str = "cognito-developer"
    
    # Account Configuration
    accounts_config_source: str = "env"  # "env" | "ssm" | "dynamodb"
    accounts_env_var: str = "ALLOWED_ACCOUNTS"
    
    class Config:
        env_file = ".env"
        case_sensitive = False
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Auto-construct JWKS URL if not provided
        if not self.jwks_url:
            self.jwks_url = (
                f"https://login.microsoftonline.com/"
                f"{self.entra_id_tenant_id}/discovery/v2.0/keys"
            )


# Global settings instance
settings = Settings()


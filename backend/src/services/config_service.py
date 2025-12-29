"""Configuration service for account/region management."""

import os
from typing import List, Dict, Optional
from src.config import settings
from src.utils.logger import get_logger

logger = get_logger(__name__)


class ConfigService:
    """Service for managing account and region configuration."""
    
    def __init__(self):
        self.accounts = self._load_accounts()
    
    def _load_accounts(self) -> Dict[str, Dict]:
        """Load account configuration."""
        accounts = {}
        
        if settings.accounts_config_source == "env":
            accounts_str = os.getenv(settings.accounts_env_var, "")
            if accounts_str:
                for account_id in accounts_str.split(","):
                    account_id = account_id.strip()
                    if account_id:
                        accounts[account_id] = {
                            "id": account_id,
                            "name": f"Account {account_id}",
                            "regions": self._get_all_regions()
                        }
        
        return accounts
    
    def get_accounts(self) -> List[Dict]:
        """Get list of available accounts."""
        return list(self.accounts.values())
    
    def get_account(self, account_id: str) -> Optional[Dict]:
        """Get account by ID."""
        return self.accounts.get(account_id)
    
    def _get_all_regions(self) -> List[str]:
        """Get list of all AWS regions."""
        return [
            "us-east-1", "us-east-2", "us-west-1", "us-west-2",
            "eu-west-1", "eu-west-2", "eu-west-3", "eu-central-1",
            "ap-southeast-1", "ap-southeast-2", "ap-northeast-1", "ap-northeast-2",
            "ap-south-1", "ca-central-1", "sa-east-1"
        ]


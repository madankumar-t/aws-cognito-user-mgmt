"""AWS STS service for cross-account access."""

import boto3
from botocore.exceptions import ClientError
from typing import Dict
from datetime import datetime, timedelta
from src.config import settings
from src.utils.logger import get_logger
from src.utils.exceptions import STSServiceException

logger = get_logger(__name__)


class STSService:
    """Service for AWS STS AssumeRole operations."""
    
    def __init__(self):
        self.sts_client = boto3.client("sts")
        self.credential_cache: Dict[str, Dict] = {}
        self.cache_ttl = timedelta(minutes=55)  # Refresh before 1-hour expiration
    
    async def assume_role(
        self,
        account_id: str,
        region: str,
        user_id: str
    ) -> Dict:
        """
        Assume IAM role in target account.
        Returns temporary credentials with caching.
        """
        cache_key = f"{account_id}:{region}:{user_id}"
        
        # Check cache
        if cache_key in self.credential_cache:
            cached = self.credential_cache[cache_key]
            expires_at = cached.get("expires_at")
            if expires_at and datetime.now() < expires_at:
                logger.debug("using_cached_credentials", extra={"account_id": account_id})
                return cached["credentials"]
        
        # Assume role
        role_arn = self._get_role_arn(account_id)
        session_name = f"CognitoMgmt-{user_id[:32]}"  # Max 64 chars, remove special chars
        
        try:
            response = self.sts_client.assume_role(
                RoleArn=role_arn,
                RoleSessionName=session_name,
                DurationSeconds=3600  # 1 hour
            )
            
            credentials = response["Credentials"]
            expiration = credentials["Expiration"]
            
            # Calculate expiration time
            if isinstance(expiration, datetime):
                expires_at = expiration
            else:
                expires_at = datetime.fromtimestamp(expiration.timestamp())
            
            # Cache credentials
            self.credential_cache[cache_key] = {
                "credentials": {
                    "AccessKeyId": credentials["AccessKeyId"],
                    "SecretAccessKey": credentials["SecretAccessKey"],
                    "SessionToken": credentials["SessionToken"]
                },
                "expires_at": expires_at
            }
            
            logger.info(
                "role_assumed",
                extra={
                    "account_id": account_id,
                    "role_arn": role_arn,
                    "session_name": session_name
                }
            )
            
            return self.credential_cache[cache_key]["credentials"]
            
        except ClientError as e:
            error_code = e.response.get("Error", {}).get("Code", "Unknown")
            logger.error(
                "assume_role_failed",
                extra={
                    "account_id": account_id,
                    "error_code": error_code,
                    "error": str(e)
                }
            )
            raise STSServiceException(f"Failed to assume role: {error_code}")
        except Exception as e:
            logger.error("assume_role_unexpected_error", extra={"error": str(e)}, exc_info=True)
            raise STSServiceException(f"Unexpected error assuming role: {str(e)}")
    
    def get_cognito_client(
        self,
        account_id: str,
        region: str,
        credentials: Dict
    ) -> boto3.client:
        """Create boto3 Cognito client with temporary credentials."""
        return boto3.client(
            "cognito-idp",
            region_name=region,
            aws_access_key_id=credentials["AccessKeyId"],
            aws_secret_access_key=credentials["SecretAccessKey"],
            aws_session_token=credentials["SessionToken"]
        )
    
    def _get_role_arn(self, account_id: str) -> str:
        """Construct IAM role ARN for target account."""
        return f"arn:aws:iam::{account_id}:role/{settings.account_role_name}"


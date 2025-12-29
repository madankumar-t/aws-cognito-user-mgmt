"""JWT authentication middleware."""

from fastapi import Request, HTTPException, status
from jose import jwt, JWTError
import httpx
from typing import Dict, List
from src.config import settings
from src.utils.logger import get_logger
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
import base64

logger = get_logger(__name__)


class JWTAuthMiddleware:
    """Middleware for JWT token validation."""
    
    def __init__(self):
        self.jwks_cache: Dict[str, str] = {}
        self.role_mapping = {
            settings.admin_group_name: "Admin",
            settings.developer_group_name: "Developer"
        }
    
    async def __call__(self, request: Request, call_next):
        """Validate JWT token for protected routes."""
        # Skip auth for health check and public routes
        if request.url.path in ["/health", "/", "/docs", "/openapi.json", "/redoc"]:
            return await call_next(request)
        
        # Extract token from Authorization header
        authorization = request.headers.get("Authorization")
        if not authorization or not authorization.startswith("Bearer "):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Missing or invalid authorization header"
            )
        
        token = authorization.split(" ")[1]
        
        try:
            # Validate token and extract claims
            claims = await self.validate_token(token)
            
            # Extract roles
            roles = self.extract_roles(claims)
            
            # Attach user info to request state
            request.state.user = {
                "sub": claims.get("sub"),
                "email": claims.get("email"),
                "name": claims.get("name"),
                "roles": roles,
                "claims": claims
            }
            
            logger.info(
                "user_authenticated",
                extra={
                    "user_id": claims.get("sub"),
                    "email": claims.get("email"),
                    "roles": roles
                }
            )
            
        except JWTError as e:
            logger.warning("jwt_validation_failed", extra={"error": str(e)})
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token"
            )
        except Exception as e:
            logger.error("auth_error", extra={"error": str(e)}, exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication failed"
            )
        
        return await call_next(request)
    
    async def validate_token(self, token: str) -> Dict:
        """Validate JWT token and return claims."""
        # Decode token header to get key ID
        try:
            unverified_header = jwt.get_unverified_header(token)
            kid = unverified_header.get("kid")
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token format"
            )
        
        # Get signing key from JWKS
        signing_key = await self.get_signing_key(kid)
        
        # Verify and decode token
        try:
            issuer = f"https://login.microsoftonline.com/{settings.entra_id_tenant_id}/v2.0"
            claims = jwt.decode(
                token,
                signing_key,
                algorithms=["RS256"],
                audience=settings.entra_id_audience,
                issuer=issuer
            )
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired"
            )
        except jwt.JWTClaimsError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Token validation failed: {str(e)}"
            )
        
        return claims
    
    async def get_signing_key(self, kid: str) -> str:
        """Get signing key from JWKS endpoint."""
        # Check cache first
        if kid in self.jwks_cache:
            return self.jwks_cache[kid]
        
        # Fetch JWKS
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(settings.jwks_url, timeout=10.0)
                response.raise_for_status()
                jwks = response.json()
        except Exception as e:
            logger.error("jwks_fetch_failed", extra={"error": str(e)})
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to fetch signing keys"
            )
        
        # Find matching key
        for key in jwks.get("keys", []):
            if key.get("kid") == kid:
                try:
                    # Construct RSA public key
                    n_bytes = base64.urlsafe_b64decode(key["n"] + "==")
                    e_bytes = base64.urlsafe_b64decode(key["e"] + "==")
                    
                    n_int = int.from_bytes(n_bytes, "big")
                    e_int = int.from_bytes(e_bytes, "big")
                    
                    public_key = rsa.RSAPublicNumbers(e_int, n_int).public_key()
                    
                    pem = public_key.public_bytes(
                        encoding=serialization.Encoding.PEM,
                        format=serialization.PublicFormat.SubjectPublicKeyInfo
                    )
                    
                    self.jwks_cache[kid] = pem.decode("utf-8")
                    return self.jwks_cache[kid]
                except Exception as e:
                    logger.error("key_construction_failed", extra={"error": str(e)})
                    continue
        
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Signing key not found"
        )
    
    def extract_roles(self, claims: Dict) -> List[str]:
        """Extract roles from token groups claim."""
        groups = claims.get("groups", [])
        roles = []
        
        for group in groups:
            if group in self.role_mapping:
                roles.append(self.role_mapping[group])
        
        return roles


# Dependency for getting current user
async def get_current_user(request: Request) -> Dict:
    """Dependency to get current authenticated user."""
    if not hasattr(request.state, "user"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    return request.state.user


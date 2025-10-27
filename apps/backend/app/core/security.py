from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import jwt
from passlib.context import CryptContext
from passlib.hash import bcrypt
import secrets
import re
from email_validator import validate_email, EmailNotValidError

from app.core.config import settings


# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class SecurityUtils:
    """Security utilities for password hashing and JWT token management"""
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a password using bcrypt"""
        return pwd_context.hash(password)
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        return pwd_context.verify(plain_password, hashed_password)
    
    @staticmethod
    def validate_password_strength(password: str) -> Dict[str, Any]:
        """
        Validate password strength according to security requirements
        Returns dict with validation results
        """
        errors = []
        
        # Minimum length check
        if len(password) < 8:
            errors.append("Password must be at least 8 characters long")
        
        # Maximum length check
        if len(password) > 128:
            errors.append("Password must be less than 128 characters long")
        
        # Character type checks
        if not re.search(r"[a-z]", password):
            errors.append("Password must contain at least one lowercase letter")
        
        if not re.search(r"[A-Z]", password):
            errors.append("Password must contain at least one uppercase letter")
        
        if not re.search(r"\d", password):
            errors.append("Password must contain at least one digit")
        
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
            errors.append("Password must contain at least one special character")
        
        # Common password patterns
        common_patterns = [
            r"123456",
            r"password",
            r"qwerty",
            r"abc123",
            r"admin",
            r"letmein"
        ]
        
        for pattern in common_patterns:
            if re.search(pattern, password.lower()):
                errors.append("Password contains common patterns and is not secure")
                break
        
        return {
            "is_valid": len(errors) == 0,
            "errors": errors,
            "strength_score": max(0, 100 - (len(errors) * 20))
        }
    
    @staticmethod
    def validate_email_format(email: str) -> Dict[str, Any]:
        """Validate email format and deliverability"""
        try:
            # Validate and get normalized result
            valid = validate_email(email)
            return {
                "is_valid": True,
                "normalized_email": valid.email,
                "errors": []
            }
        except EmailNotValidError as e:
            return {
                "is_valid": False,
                "normalized_email": None,
                "errors": [str(e)]
            }
    
    @staticmethod
    def generate_jwt_token(
        data: Dict[str, Any],
        expires_delta: Optional[timedelta] = None,
        token_type: str = "access"
    ) -> str:
        """Generate JWT token with expiration"""
        to_encode = data.copy()
        
        # Set expiration time
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            # Default expiration times
            if token_type == "access":
                expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
            else:  # refresh token
                expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        
        # Add standard claims
        to_encode.update({
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": token_type,
            "jti": secrets.token_urlsafe(32)  # JWT ID for blacklisting
        })
        
        # Encode token
        encoded_jwt = jwt.encode(
            to_encode,
            settings.SECRET_KEY,
            algorithm=settings.ALGORITHM
        )
        
        return encoded_jwt
    
    @staticmethod
    def decode_jwt_token(token: str) -> Dict[str, Any]:
        """Decode and validate JWT token"""
        try:
            payload = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=[settings.ALGORITHM]
            )
            return {
                "is_valid": True,
                "payload": payload,
                "error": None
            }
        except jwt.ExpiredSignatureError:
            return {
                "is_valid": False,
                "payload": None,
                "error": "Token has expired"
            }
        except jwt.InvalidTokenError as e:
            return {
                "is_valid": False,
                "payload": None,
                "error": f"Invalid token: {str(e)}"
            }
    
    @staticmethod
    def extract_token_jti(token: str) -> Optional[str]:
        """Extract JWT ID (jti) from token without full validation"""
        try:
            # Decode without verification to get jti for blacklisting
            payload = jwt.decode(
                token,
                options={"verify_signature": False, "verify_exp": False}
            )
            return payload.get("jti")
        except Exception:
            return None
    
    @staticmethod
    def generate_secure_random_string(length: int = 32) -> str:
        """Generate cryptographically secure random string"""
        return secrets.token_urlsafe(length)
    
    @staticmethod
    def generate_verification_code(length: int = 6) -> str:
        """Generate numeric verification code"""
        return ''.join(secrets.choice('0123456789') for _ in range(length))


# Convenience functions
def hash_password(password: str) -> str:
    """Hash password - convenience function"""
    return SecurityUtils.hash_password(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password - convenience function"""
    return SecurityUtils.verify_password(plain_password, hashed_password)


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Create access token - convenience function"""
    return SecurityUtils.generate_jwt_token(data, expires_delta, "access")


def create_refresh_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Create refresh token - convenience function"""
    return SecurityUtils.generate_jwt_token(data, expires_delta, "refresh")
"""Authentication utilities."""
from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.config import settings

# Initialize password context
# Note: There's a known issue with passlib 1.7.4 and certain bcrypt versions
# where bug detection during initialization can fail. This is handled in get_password_hash.
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password."""
    # Bcrypt has a 72-byte limit, truncate if necessary
    password_bytes = password.encode('utf-8')
    if len(password_bytes) > 72:
        # Truncate to 72 bytes, handling multi-byte characters
        password = password_bytes[:72].decode('utf-8', errors='ignore')
    
    # Workaround for passlib/bcrypt initialization issue
    # The error can occur during backend initialization's bug detection phase
    max_retries = 3
    for attempt in range(max_retries):
        try:
            return pwd_context.hash(password)
        except ValueError as e:
            error_msg = str(e)
            # Handle bcrypt password length errors
            if "password cannot be longer than 72 bytes" in error_msg:
                if attempt < max_retries - 1:
                    # Further truncate and retry
                    password = password[:50]
                    continue
                else:
                    # Last attempt - use a safe fallback length
                    password = password[:40]
                    return pwd_context.hash(password)
            # Re-raise if it's a different ValueError
            raise
        except Exception:
            # For other exceptions (like initialization issues), retry once
            if attempt < max_retries - 1:
                continue
            raise


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_expire_minutes)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    return encoded_jwt


def decode_access_token(token: str) -> Optional[dict]:
    """Decode and verify a JWT token."""
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        return payload
    except JWTError:
        return None




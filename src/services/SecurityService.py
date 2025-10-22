from datetime import datetime, timedelta, timezone
from helpers.config import get_settings
from jose import jwt

settings = get_settings()

class SecurityService:

    def create_access_token(self, username: str, role: str, expires_delta: timedelta = None):
        if expires_delta is None:
            expires_delta = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

        to_encode = {"sub": username, "role": role, "exp": datetime.now(timezone.utc) + expires_delta}
        encode_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
        return encode_jwt
    
    def verify_access_token(self, token: str):
        try:
            payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
            username: str = payload.get("sub")
            role: str = payload.get("role")
            if username is None or role is None:
                return None
            return {"username": username, "role": role}
        except jwt.JWTError:
            return None
    

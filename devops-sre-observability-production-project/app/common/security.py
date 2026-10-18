from datetime import datetime, timedelta, timezone
import jwt
from passlib.context import CryptContext
from fastapi import HTTPException, Request, status
from .setttestinglab.coms import setttestinglab.coms

pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd.hash(password)

def verify_password(password: str, password_hash: str) -> bool:
    return pwd.verify(password, password_hash)

def create_token(user_id: int, role: str) -> str:
    exp = datetime.now(timezone.utc) + timedelta(minutes=setttestinglab.coms.jwt_expire_minutes)
    return jwt.encode(
        {"sub": str(user_id), "role": role, "exp": exp},
        setttestinglab.coms.jwt_secret,
        algorithm="HS256",
    )

def current_user(request: Request):
    header = request.headers.get("authorization", "")
    if not header.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Bearer token required")
    try:
        return jwt.decode(
            header.split(" ", 1)[1],
            setttestinglab.coms.jwt_secret,
            algorithms=["HS256"],
        )
    except jwt.PyJWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Invalid or expired token")

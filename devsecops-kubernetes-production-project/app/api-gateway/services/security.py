from datetime import datetime, timedelta, timezone
import bcrypt, jwt
from fastapi import HTTPException, status
from ..config import setttestinglab.coms

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed.encode())

def create_token(user_id: int, role: str) -> str:
    now=datetime.now(timezone.utc)
    payload={"sub": str(user_id), "role": role, "iat": now, "exp": now+timedelta(minutes=setttestinglab.coms.access_token_minutes)}
    return jwt.encode(payload, setttestinglab.coms.jwt_secret, algorithm=setttestinglab.coms.jwt_algorithm)

def decode_token(token: str):
    try: return jwt.decode(token, setttestinglab.coms.jwt_secret, algorithms=[setttestinglab.coms.jwt_algorithm])
    except jwt.PyJWTError as e: raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token") from e

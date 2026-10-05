from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel, EmailStr, Field
from prometheus_fastapi_instrumentator import Instrumentator
from app.common.db import db
from app.common.security import hash_password, verify_password, create_token, current_user
from app.common.telemetry import instrument_app

app = FastAPI(title="User Service")
instrument_app(app)
Instrumentator().instrument(app).expose(app)

class Register(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    name: str = Field(min_length=2, max_length=100)

class Login(BaseModel):
    email: EmailStr
    password: str

@app.get("/health")
def health(): return {"status":"ok","service":"user-service"}

@app.get("/ready")
def ready():
    with db() as conn: conn.execute("SELECT 1")
    return {"status":"ready"}

@app.post("/users/register", status_code=201)
def register(payload: Register):
    with db() as conn:
        if conn.execute("SELECT id FROM users WHERE email=%s", (payload.email,)).fetchone():
            raise HTTPException(409, "Email already registered")
        return conn.execute(
            """INSERT INTO users(email,password_hash,name,role)
               VALUES(%s,%s,%s,'USER')
               RETURNING id,email,name,role""",
            (payload.email, hash_password(payload.password), payload.name),
        ).fetchone()

@app.post("/users/login")
def login(payload: Login):
    with db() as conn:
        user = conn.execute(
            "SELECT id,email,password_hash,name,role FROM users WHERE email=%s",
            (payload.email,),
        ).fetchone()
    if not user or not verify_password(payload.password, user["password_hash"]):
        raise HTTPException(401, "Invalid credentials")
    return {
        "access_token": create_token(user["id"], user["role"]),
        "token_type": "bearer",
        "user": {"id":user["id"],"name":user["name"],"role":user["role"]},
    }

@app.get("/users/me")
def me(request: Request):
    claims = current_user(request)
    with db() as conn:
        user = conn.execute(
            "SELECT id,email,name,role,created_at FROM users WHERE id=%s",
            (int(claims["sub"]),),
        ).fetchone()
    if not user:
        raise HTTPException(404, "User not found")
    return user

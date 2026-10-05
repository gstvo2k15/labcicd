from fastapi import FastAPI
from pydantic import BaseModel
import os
import socket
import psycopg

app = FastAPI(title="K8s Docker ECR Backend", version="1.0.0")

class Message(BaseModel):
    message: str

def db_dsn():
    return os.getenv("DATABASE_URL", "postgresql://appuser:apppassword@db:5432/appdb")

def ensure_table():
    with psycopg.connect(db_dsn(), connect_timeout=3) as conn:
        conn.execute("CREATE TABLE IF NOT EXISTS messages (id SERIAL PRIMARY KEY, message TEXT NOT NULL)")
        conn.commit()

@app.get("/health")
def health():
    return {"status": "ok", "service": "backend", "hostname": socket.gethostname()}

@app.get("/ready")
def ready():
    try:
        ensure_table()
        return {"status": "ready", "database": "ok"}
    except Exception as exc:
        return {"status": "not-ready", "database": "error", "detail": str(exc)}

@app.get("/api/info")
def info():
    return {"service": "backend", "environment": os.getenv("APP_ENV", "local"), "version": os.getenv("APP_VERSION", "1.0.0")}

@app.get("/api/messages")
def messages():
    ensure_table()
    with psycopg.connect(db_dsn(), connect_timeout=3) as conn:
        rows = conn.execute("SELECT id, message FROM messages ORDER BY id DESC LIMIT 20").fetchall()
    return [{"id": r[0], "message": r[1]} for r in rows]

@app.post("/api/echo")
def echo(payload: Message):
    ensure_table()
    with psycopg.connect(db_dsn(), connect_timeout=3) as conn:
        conn.execute("INSERT INTO messages (message) VALUES (%s)", (payload.message,))
        conn.commit()
    return {"message": payload.message, "service": "backend"}
